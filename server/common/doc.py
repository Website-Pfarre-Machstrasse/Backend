import copy
import functools

from flask_apispec import FlaskApiSpec as Base
from flask_apispec.apidoc import Converter as BaseConverter
from flask_apispec.extension import make_apispec
from flask_apispec.paths import CONVERTER_MAPPING, DEFAULT_TYPE
from flask_apispec.utils import resolve_resource, merge_recursive, resolve_annotations
from marshmallow import Schema
from marshmallow.utils import is_instance_or_subclass


def argument_to_param(argument, rule, override=None, *, major_api_version=2):
    param = {
        'in': 'path',
        'name': argument,
        'required': True,
    }
    type_, format_ = CONVERTER_MAPPING.get(type(rule._converters[argument]), DEFAULT_TYPE)
    schema = {'type': type_}
    if format_ is not None:
        schema['format'] = format_
    if rule.defaults and argument in rule.defaults:
        param['default'] = rule.defaults[argument]
    if major_api_version == 2:
        param.update(schema)
    elif major_api_version == 3:
        param['schema'] = schema
    else:
        raise NotImplementedError("No support for OpenAPI / Swagger Major version {}".format(major_api_version))
    param.update(override or {})
    return param


def rule_to_params(rule, overrides=None, *, major_api_version=2):
    overrides = (overrides or {})
    result = [
        argument_to_param(argument, rule, overrides.get(argument, {}), major_api_version=major_api_version)
        for argument in rule.arguments
    ]
    for key in overrides.keys():
        if overrides[key].get('in') in ('header', 'query'):
            overrides[key]['name'] = overrides[key].get('name', key)
            result.append(overrides[key])
    return result


class Converter(BaseConverter):
    def get_operation(self, rule, view, parent=None):
        annotation = resolve_annotations(view, 'docs', parent)
        docs = merge_recursive(annotation.options)
        operation = {
            'responses': self.get_responses(view, parent, docs),
            'parameters': self.get_parameters(rule, view, docs, parent),
        }
        docs.pop('params', None)
        return merge_recursive([operation, docs])

    def get_parameters(self, rule, view, docs: dict, parent=None):
        openapi = self.marshmallow_plugin.converter
        annotation = resolve_annotations(view, 'args', parent)
        extra_params = []
        for args in annotation.options:
            schema = args.get('args', {})
            openapi_converter = openapi.schema2parameters
            if not is_instance_or_subclass(schema, Schema):
                if callable(schema):
                    schema = schema(request=None)
                else:
                    schema = Schema.from_dict(schema)
                    openapi_converter = functools.partial(
                        self._convert_dict_schema, openapi_converter)

            options = copy.copy(args.get('kwargs', {}))
            if not options.get('location'):
                options['location'] = 'body'

            if options['location'] == 'body' and self.spec.openapi_version.major < 3:
                extra_params += openapi_converter(schema, **options) if args else []
            else:
                content_type = options.pop('content_type', 'application/json')
                description = options.pop('description', '')
                required = options.pop('required', True)
                docs['requestBody'] = {
                    'description': description,
                    'required': required,
                    'content': {
                        content_type: {
                            'schema': schema
                        }
                    }
                } if args else {}

        rule_params = rule_to_params(rule, docs.get('params'), major_api_version=self.spec.openapi_version.major) or []

        return extra_params + rule_params

    def get_responses(self, view, parent=None, docs=None):
        annotation = resolve_annotations(view, 'schemas', parent)
        options = []
        for option in annotation.options:
            exploded = {}
            for status_code, meta in option.items():
                if self.spec.openapi_version.major < 3:
                    content_type = meta.pop('content_type', None)
                    if content_type:
                        docs.setdefault('produces', []).append(content_type)
                    exploded[status_code] = meta
                else:
                    content_type = meta.get('content_type', None)
                    if not content_type:
                        content_type = list(self.app.extensions['restful'].representations.keys())
                    if isinstance(content_type, (list, tuple, set)):
                        content_types = content_type
                    else:
                        content_types = [content_type]
                    (exploded
                        .setdefault(status_code, {})
                        .setdefault('content', {})
                        .update({
                            content_type: {
                               'schema': meta['schema']
                            } for content_type in content_types
                        })
                     )
                    exploded[status_code]['description'] = meta.get('description', '')
            options.append(exploded)
        return merge_recursive(options)

    def get_request_body(self, rule, view, docs, parent):
        pass


class ViewConverter(Converter):
    def get_operations(self, rule, view):
        return {method: view for method in rule.methods}


class ResourceConverter(Converter):
    def get_operations(self, rule, resource):
        return {
            method: getattr(resource, method.lower())
            for method in rule.methods
            if hasattr(resource, method.lower())
        }

    def get_parent(self, resource, **kwargs):
        return resolve_resource(resource, **kwargs)


class FlaskApiSpec(Base):
    @property
    def handlers(self):
        return {'application/json': self.spec.to_dict, 'application/yaml': self.spec.to_yaml}

    def init_app(self, app):
        self.app = app
        self.spec = self.app.config.get('APISPEC_SPEC') or \
                    make_apispec(self.app.config.get('APISPEC_TITLE', 'flask-apispec'),
                                 self.app.config.get('APISPEC_VERSION', 'v1'),
                                 self.app.config.get('APISPEC_OAS_VERSION', '2.0'))
        self.add_swagger_routes()
        self.resource_converter = ResourceConverter(self.app, self.spec, self.document_options)
        self.view_converter = ViewConverter(self.app, self.spec, self.document_options)

        for deferred in self._deferred:
            deferred()

    def swagger_json(self):
        from flask import request
        mime_type = request.accept_mimetypes.best_match(self.handlers.keys(), 'application/json')
        return self.handlers[mime_type]()


doc = FlaskApiSpec()
