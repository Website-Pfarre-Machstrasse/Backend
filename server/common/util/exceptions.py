from werkzeug.exceptions import HTTPException

__all__ = ['AuthorisationError',
           'AuthenticationError',
           'ServerError',
           'RequestError',
           'UserNotFoundError']


class CustomHTTPException(HTTPException):

    def __init__(self, message: str, extra=None):
        self.message = message
        self.extra = extra
        self.response = None

    @property
    def data(self):
        data = {'status': self.code, 'message': self.message}
        if self.extra:
            data['extra'] = self.extra
        return data

    def __str__(self):
        code = self.code if self.code is not None else "???"
        return "%s %s: %s" % (code, self.name, self.message)

    def __repr__(self):
        code = self.code if self.code is not None else "???"
        return "<%s '%s: %s'>" % (self.__class__.__name__, code, self.name)


class RequestError(CustomHTTPException):
    code = 400


class AuthorisationError(CustomHTTPException):
    code = 401


class AuthenticationError(CustomHTTPException):
    code = 401


class ServerError(CustomHTTPException):
    code = 500
    response = None

    def __init__(self, error: Exception):
        super(ServerError, self).__init__(str(error))


class UserNotFoundError(CustomHTTPException):
    def __init__(self, identity):
        super(UserNotFoundError, self).__init__('User not found', extra=identity)
