import re
from functools import wraps

import flask
import werkzeug
from flask_apispec import doc, use_kwargs, utils
from flask_apispec.annotations import annotate
from flask_apispec.wrapper import Wrapper as OriginalWrapper, identity, MARSHMALLOW_VERSION_INFO
from flask_apispec.wrapper import unpack, packed
from flask_jwt_extended import get_jwt_claims, jwt_required as _jwt_required
from werkzeug.exceptions import HTTPException

from .exceptions import AuthorisationError, ServerError

__all__ = ['admin_required', 'lazy_property', 'autodoc', 'write_only_property', 'tag', 'params',
           'marshal_with', 'use_kwargs', 'transactional', 'jwt_required', 'op_id']


def transactional(session):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                if session.autocommit:
                    with session.begin() as transaction:
                        kwargs.update(_transaction=transaction)
                        return fn(*args, **kwargs)
                else:
                    with session.begin_nested() as transaction:
                        kwargs.update(_transaction=transaction)
                        return fn(*args, **kwargs)
            except Exception as e:
                if isinstance(e, HTTPException):
                    raise e
                else:
                    raise ServerError(e) from e
        return wrapper
    return decorator


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        claims = get_jwt_claims()
        if claims['role'] != 'admin':
            raise AuthorisationError('Admins only!')
        else:
            return fn(*args, **kwargs)
    return jwt_required(wrapper)


def lazy_property(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    @wraps(fn)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property


def params(**kwargs):
    def decorator(fn):
        params = {}
        for k, v in kwargs.items():
            if isinstance(v, str):
                params[k] = {'description': v}
            elif isinstance(v, dict):
                params[k] = v
        return doc(params=params)(fn)
    return decorator


def tag(*tag):
    return doc(tags=[*tag])


def parse_meta(s):
    param_regex = re.compile(":param ([a-zA-Z_][0-9a-zA-Z_]*): (.*)")
    param_match = param_regex.search(s)
    param_name = param_match.group(1)
    param_description = param_match.group(2)
    return param_name, {'description': param_description}


def parse_doc(fn):
    out = {}
    if fn.__doc__:
        lines = fn.__doc__.split('\n')
        if lines[0] == '' or lines[0].isspace():
            lines.pop(0)
        if lines[-1] == '' or lines[-1].isspace():
            lines.pop()
        lines = map(str.lstrip, lines)
        lines = list(lines)
        meta = filter(lambda s: s.startswith(':'), lines)
        lines = filter(lambda s: not s.startswith(':'), lines)
        meta = map(parse_meta, meta)
        meta = dict(meta)
        summary = next(lines)
        cleaned = summary
        body = '\n'.join(lines)
        if body:
            cleaned += ('\n' + body)
        summary = summary.lstrip('#').lstrip()
        out['description'] = cleaned
        out['summary'] = summary
        if meta:
            out['parameters'] = meta
    if hasattr(fn, '__owner__'):
        clazz = fn.__owner__
        if fn.__name__ == 'get':
            out['operationId'] = 'get'+clazz.__name__
        if fn.__name__ == 'delete':
            out['operationId'] = 'delete'+clazz.__name__
        if fn.__name__ in ('patch', 'put'):
            out['operationId'] = 'update'+clazz.__name__
            if hasattr(clazz, 'put') and hasattr(clazz, 'patch'):
                if fn.__name__ == 'patch':
                    out['operationId'] += 'Partial'
                elif fn.__name__ == 'put':
                    out['operationId'] += 'Strict'
        if fn.__name__ == 'post' and hasattr(clazz, '__child__'):
            out['operationId'] = 'create'+clazz.__child__.__name__
    return out


def autodoc(fn):
    if isinstance(fn, type):
        for name in fn.__dict__:
            attr = getattr(fn, name)
            if callable(attr) and name in ('get', 'put', 'post', 'patch', 'delete'):
                attr.__owner__ = fn
                setattr(fn, name, autodoc(attr))
        if fn.__doc__:
            parsed_doc = parse_doc(fn)
            return doc(**parsed_doc)(fn)
    elif callable(fn):
        parsed_doc = parse_doc(fn)
        return doc(**parsed_doc)(fn)
    return fn


def jwt_required(fn):
    return auth_required('bearerAuth')(_jwt_required(fn))


def auth_required(security):
    return doc(security=[{security: []}])


def op_id(op_id):
    return doc(operationId=op_id)


def marshal_with(schema, code='default', description='', content_type=None, inherit=None, apply=None):
    """Marshal the return value of the decorated view function using the
    specified schema.

    Usage:

    .. code-block:: python

        class PetSchema(Schema):
            class Meta:
                fields = ('name', 'category')

        @marshal_with(PetSchema)
        def get_pet(pet_id):
            return Pet.query.filter(Pet.id == pet_id).one()

    :param schema: :class:`Schema <marshmallow.Schema>` class or instance, or `None`
    :param code: Optional HTTP response code
    :param description: Optional response description
    :param content_type: Optional response content type header (only used in OpenAPI 3.x)
    :param inherit: Inherit schemas from parent classes
    :param apply: Marshal response with specified schema
    """
    def wrapper(func):
        options = {
            code: {
                'schema': schema or {},
                'description': description,
                'content_type': content_type,
            },
        }
        annotate(func, 'schemas', [options], inherit=inherit, apply=apply)
        return activate(func)
    return wrapper


def activate(func):
    if isinstance(func, type) or getattr(func, '__apispec__', {}).get('wrapped'):
        return func

    @wraps(func)
    def wrapped(*args, **kwargs):
        instance = args[0] if func.__apispec__.get('ismethod') else None
        annotation = utils.resolve_annotations(func, 'wrapper', instance)
        wrapper_cls = utils.merge_recursive(annotation.options).get('wrapper', Wrapper)
        wrapper = wrapper_cls(func, instance)
        return wrapper(*args, **kwargs)

    wrapped.__apispec__['wrapped'] = True
    return wrapped


# noinspection PyPep8Naming
class write_only_property(property):
    # noinspection PyShadowingNames
    def __init__(self, fset=None, fget=None, fdel=None, doc=None):
        super().__init__(fget=fget, fset=fset, fdel=fdel, doc=doc)


class Wrapper(OriginalWrapper):
    def __call__(self, *args, **kwargs):
        response = self.call_view(*args, **kwargs)
        if isinstance(response, werkzeug.Response):
            return response
        rv, status_code, headers = unpack(response)
        mv, content_type = self.marshal_result(rv, status_code)
        app = flask.current_app
        api = app.extensions.get('restful', None)
        if api:
            if headers:
                content_type = headers['Content-Type'] or content_type
            if content_type:
                return api.make_response(mv, status_code, headers, fallback_mediatype=content_type)
            return api.make_response(mv, status_code, headers)
        else:
            return app.make_response(packed(mv, status_code, headers))

    def marshal_result(self, result, status_code):
        config = flask.current_app.config
        format_response = config.get('APISPEC_FORMAT_RESPONSE', flask.jsonify) or identity
        annotation = utils.resolve_annotations(self.func, 'schemas', self.instance)
        schemas = utils.merge_recursive(annotation.options)
        schema = schemas.get(status_code, schemas.get('default'))
        if schema and annotation.apply is not False:
            dumped = utils.resolve_schema(schema['schema'], request=flask.request).dump(result)
            output = dumped.data if MARSHMALLOW_VERSION_INFO[0] < 3 else dumped
        else:
            output = result

        return format_response(output), schema['content_type']
