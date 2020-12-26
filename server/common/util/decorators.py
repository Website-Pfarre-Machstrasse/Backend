from functools import wraps

from flask import Response
from flask_jwt_extended import verify_jwt_in_request, get_jwt_claims
from .exceptions import AuthorisationError
from marshmallow import Schema

__all__ = ['admin_required', 'auto_marshall', 'marshall_with', 'lazy_property']


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


def auto_marshall(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        code = 200
        headers = {}
        result = fn(*args, **kwargs)
        if type(result) is tuple:
            if len(result) == 1:
                (result) = result
            elif len(result) == 2:
                (result, code) = result
            elif len(result) == 3:
                (result, code, headers) = result

        if type(result) is Response:
            return result

        if 300 > code >= 200:
            schema = None
            if isinstance(result, list) and len(result) > 0 and hasattr(result[0], '__marshmallow__'):
                schema = result[0].__marshmallow__(many=True)
            elif hasattr(result, '__marshmallow__'):
                schema = result.__marshmallow__(many=False)
            if schema:
                return schema.dump(result), code, headers
        return result, code, headers

    return wrapper


def marshall_with(schema: Schema, many=False):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            if type(result) is tuple:
                result, code = result
                if code != 200:
                    return result
                else:
                    return schema.dump(result, many=many), code
            else:
                return schema.dump(result, many=many)
        return wrapper
    return decorator


def lazy_property(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    @wraps(fn)
    def _lazy_property(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazy_property

