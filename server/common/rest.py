from flask_apispec.views import MethodResource
from flask_restful import Resource as RestfulResource

from server.common.util.decorators import autodoc


class Resource(MethodResource, RestfulResource):
    def __init_subclass__(cls, **kwargs):
        return autodoc(cls)
