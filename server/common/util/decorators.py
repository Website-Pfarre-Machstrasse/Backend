from functools import wraps

import flask
import werkzeug
from flask_apispec import doc, use_kwargs, utils
from flask_apispec.annotations import annotate
from flask_apispec.wrapper import Wrapper as OriginalWrapper
from flask_apispec.wrapper import unpack, packed
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims

from .exceptions import AuthorisationError

__all__ = ['admin_required', 'lazy_property', 'autodoc', 'write_only_property', 'tag', 'produces', 'params',
           'marshal_with', 'use_kwargs', 'transactional']


def transactional(session):
    def decorator(fn):
        def wrapper(*args, **kwargs):
            with session.begin() as transaction:
                kwargs.update(_transaction=transaction)
                return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['role'] != 'admin':
            raise AuthorisationError('Admins only!')
        else:
            return fn(*args, **kwargs)
    return wrapper


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


def tag(tag):
    return doc(tags=[tag])


def produces(*mimetypes):
    return doc(produces=list(mimetypes))


def autodoc(fn):
    if fn.__doc__:
        return doc(description=fn.__doc__)(fn)
    return fn


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
        mv = self.marshal_result(rv, status_code)
        app = flask.current_app
        api = app.extensions.get('restful', None)
        if api:
            return api.make_response(mv, status_code, headers)
        else:
            return app.make_response(packed(mv, status_code, headers))
