import re

import sqlalchemy as sa
from apispec.ext.marshmallow import MarshmallowPlugin as BaseMarshmallowPlugin, OpenAPIConverter, SchemaResolver
from apispec.ext.marshmallow.common import get_fields, resolve_schema_cls, resolve_schema_instance
from flask_marshmallow.fields import Hyperlinks
from marshmallow import Schema, fields, validate
from marshmallow.schema import SchemaMeta
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import ModelConverter as BaseModelConverter
from werkzeug.routing import Rule

from server.common.doc import doc
from server.common.schema.custom_fields import FileField

special_names = {
    'collection_post': 'create',
    'collection_get': 'get_all',
    'self_delete': 'delete',
    'self_get': 'get',
    'self_patch': 'modify_partial',
    'self_put': 'modify_strict'
}


class ModelConverter(BaseModelConverter):
    def __init__(self, schema_cls=None):
        super().__init__(schema_cls)
        self.SQLA_TYPE_MAPPING[sa.Enum] = EnumField

    def _add_column_kwargs(self, kwargs, column):
        super(ModelConverter, self)._add_column_kwargs(kwargs, column)
        if hasattr(column, 'type') and isinstance(column.type, sa.Enum):
            kwargs['enum'] = column.type.enum_class
            kwargs['metadata']['doc_default'] = column.default.arg
            kwargs['validate'] = list(
                filter(
                    lambda v: not isinstance(v, (validate.Length, validate.OneOf)),
                    kwargs['validate']
                )
            )


# noinspection PyUnusedLocal
def enum2properties(self, field, **kwargs):
    """
    Add an OpenAPI extension for marshmallow_enum.EnumField instances
    """
    ret = {}
    if isinstance(field, EnumField):
        if field.by_value:
            enum = [m.value for m in field.enum]
        else:
            enum = [m.name for m in field.enum]
        ret['enum'] = enum
    return {}


# noinspection PyUnusedLocal
def tuple2properties(self, field, **kwargs):
    """
    Add an OpenAPI extension for marshmallow.fields.Tuple instances
    """
    ret = {}
    if isinstance(field, fields.Tuple):
        if self.openapi_version.major >= 3 and self.openapi_version.minor >= 1:
            ret["items"] = list(map(self.field2property, field.tuple_fields))
            ret["minItems"] = len(field.tuple_fields)
            ret["additionalItems"] = False
        else:
            ret["items"] = {'oneOf': list(map(self.field2property, field.tuple_fields))}
            ret["minItems"] = len(field.tuple_fields)
            ret["maxItems"] = len(field.tuple_fields)
    return ret


def make_link(rule, field, method='get'):
    rule = rule.replace('/', '~1')
    link = {
        'operationRef': f"#/paths/{rule}/{method}"
    }
    if field.values and len(field.values) > 0:
        link['parameters'] = {}
        for k, v in field.values.items():
            v = v.replace("<", "").replace(">", "")
            link['parameters'][k] = '$response.body#/'+v
    return link


def resolve_link(name: str, field, rule: Rule, links: dict):
    rule_regex = re.compile('<[^:]*:([^>]*)>')
    _rule = rule_regex.sub(r'{\1}', rule.rule)
    if len(rule.methods) == 1 and rule.methods[0] == 'GET':
        if name in special_names:
            name = special_names[name]
        links[name] = make_link(_rule, field)
    else:
        for method in rule.methods:  # type: str
            if method in ('HEAD', 'OPTIONS'):
                continue
            method = method.lower()
            _name = f'{name}_{method}'
            if _name in special_names:
                _name = special_names[_name]
            links[_name] = make_link(_rule, field, method)


def resolve_links(schema):
    if not isinstance(schema, (Schema, SchemaMeta)):
        return {}
    fields = get_fields(schema)
    if '_links' not in fields:
        return {}
    _links = fields['_links']  # type: Hyperlinks
    if not isinstance(_links, Hyperlinks):
        return {}
    links = {}
    for name, field in _links.schema.items():
        # noinspection PyProtectedMember
        rules = doc.app.url_map._rules_by_endpoint[field.endpoint]
        if len(rules) == 0:
            continue
        elif len(rules) == 1:
            resolve_link(name, field, rules[0], links)
        else:
            for i, rule in enumerate(rules):
                resolve_link(name + str(i), field, rule, links)
    return links


class Resolver(SchemaResolver):
    def resolve_schema(self, data):
        """Resolve marshmallow Schemas in an OpenAPI component or header -
        modifies the input dictionary to translate marshmallow Schemas to OpenAPI
        Schema Objects or Reference Objects.

        OpenAPIv3 Components: ::

            #Input
            {
                "description": "user to add to the system",
                "content": {
                    "application/json": {
                        "schema": "UserSchema"
                    }
                }
            }

            #Output
            {
                "description": "user to add to the system",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/User"
                        }
                    }
                }
            }

        :param dict|str data: either a parameter or response dictionary that may
            contain a schema, or a reference provided as string
        """
        if not isinstance(data, dict):
            return

        # OAS 2 component or OAS 3 header
        if "schema" in data:
            data["schema"] = self.resolve_schema_dict(data["schema"])
        # OAS 3 component except header
        if self.openapi_version.major >= 3:
            if "content" in data:
                links = {}
                for content in data["content"].values():
                    if "schema" in content:
                        links.update(resolve_links(content["schema"]))
                        schema = self.resolve_schema_dict(content["schema"])
                        content["schema"] = schema
                if links:
                    data['links'] = links


class Converter(OpenAPIConverter):
    def __init__(self, openapi_version, schema_name_resolver, spec):
        self.field_mapping[FileField] = ("string", "binary")
        self.field_mapping[Hyperlinks] = ("object", None)
        self.field_mapping[EnumField] = ("string", None)
        self.field_mapping[fields.Tuple] = ("array", None)
        super().__init__(openapi_version, schema_name_resolver, spec)


class MarshmallowPlugin(BaseMarshmallowPlugin):
    Resolver = Resolver
    Converter = Converter

    def operation_helper(self, operations, **kwargs):
        for operation in operations.values():
            if not isinstance(operation, dict):
                continue
            if "parameters" in operation:
                operation["parameters"] = self.resolver.resolve_parameters(
                    operation["parameters"]
                )
            if self.openapi_version.major >= 3:
                if "requestBody" in operation:
                    self.resolver.resolve_schema(operation["requestBody"])
                    operation["requestBody"].pop('links', None)
            for response in operation.get("responses", {}).values():
                self.resolver.resolve_response(response)


def resolver(schema):
    """Default schema name resolver function that strips 'Schema' from the end of the class name."""
    schema_cls = resolve_schema_cls(schema)
    name = schema_cls.__name__
    if name.endswith("Schema"):
        name = name[:-6] or name
    schema_inst = resolve_schema_instance(schema)
    if schema_inst.partial:
        return f'{name}_partial'
    if schema_inst.only:
        return f'{name}.{"-".join(schema_inst.only)}'
    return name
