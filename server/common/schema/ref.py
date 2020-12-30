import re

import sqlalchemy as sa
from apispec.ext.marshmallow import MarshmallowPlugin as BaseMarshmallowPlugin, OpenAPIConverter, SchemaResolver
from apispec.ext.marshmallow.common import get_fields
from flask_marshmallow import Marshmallow
from flask_marshmallow.fields import Hyperlinks, URLFor
from marshmallow import Schema
from marshmallow.schema import SchemaMeta
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import ModelConverter as BaseModelConverter

__all__ = ['ma', 'ModelConverter', 'marshmallow_plugin', 'enum2properties', 'hyperlinks2properties', 'urlfor2properties']

from werkzeug.routing import Rule

from common.doc import doc

ma = Marshmallow()


class ModelConverter(BaseModelConverter):
    def __init__(self, schema_cls=None):
        super().__init__(schema_cls)
        self.SQLA_TYPE_MAPPING[sa.Enum] = EnumField

    def _add_column_kwargs(self, kwargs, column):
        super(ModelConverter, self)._add_column_kwargs(kwargs, column)
        if hasattr(column, 'type') and isinstance(column.type, sa.Enum):
            kwargs['enum'] = column.type.enum_class


def enum2properties(self, field, **kwargs):
    """
    Add an OpenAPI extension for marshmallow_enum.EnumField instances
    """
    if isinstance(field, EnumField):
        return {'type': 'string', 'enum': [m.name for m in field.enum]}
    return {}


def hyperlinks2properties(self: OpenAPIConverter, field, **kwargs):
    """
    Add an OpenAPI extension for flask_marshmallow.fields.Hyperlinks instances
    """
    if isinstance(field, Hyperlinks):
        return {'type': 'object'}
    return {}


def urlfor2properties(self: OpenAPIConverter, field, **kwargs):
    """
    Add an OpenAPI extension for flask_marshmallow.fields.URLFor instances
    """
    if isinstance(field, URLFor):
        rules = doc.app.url_map._rules_by_endpoint[field.endpoint]
        if len(rules) == 1:
            rule = rules[0]  # type: Rule
            _rule = re.compile('<[^:]*:([^>]*)>').sub(r'{\1}', rule.rule)
            return {
                'type': 'string',
                'format': _rule
            }
    return {}


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
                        links.update(self.resolve_links(content["schema"]))
                        schema = self.resolve_schema_dict(content["schema"])
                        content["schema"] = schema
                if links:
                    data['links'] = links

    def resolve_links(self, schema):
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
            rules = doc.app.url_map._rules_by_endpoint[field.endpoint]
            if len(rules) == 0:
                continue
            elif len(rules) == 1:
                rule = rules[0]  # type: Rule
                _rule = re.compile('<[^:]*:([^>]*)>').sub(r'{\1}', rule.rule)
                links[name] = {
                    'operationRef': f"#/paths/{_rule.replace('/', '~1')}/get"
                }
                if field.values and len(field.values) > 0:
                    links[name]['parameters'] = {
                        k: f'$response.body#/{v.replace("<", "").replace(">", "")}' for k, v in field.values.items()
                    }
            else:
                for i, rule in enumerate(rules):
                    _rule = re.compile('<[^:]*:([^>]*)>').sub(r'{\1}', rule.rule)
                    links[name+str(i)] = {
                        'operationRef': f"#/paths/{_rule.replace('/', '~1')}/get"
                    }
                    if field.values and len(field.values) > 0:
                        links[name+str(i)]['parameters'] = {
                            k: f'$response.body#/{v.replace("<", "").replace(">", "")}' for k, v in field.values.items()
                        }
        return links


class MarshmallowPlugin(BaseMarshmallowPlugin):
    Resolver = Resolver

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


marshmallow_plugin = MarshmallowPlugin()
