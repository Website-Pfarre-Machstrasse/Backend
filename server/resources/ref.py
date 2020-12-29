from flask import make_response
from flask_restful import Api

__all__ = ['api']

api = Api(prefix='/api')


@api.representation('text/markdown')
def text_repr(resp, code, header=None):
    return make_response(resp, code, header)
