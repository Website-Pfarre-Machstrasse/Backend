from flask_restful import Resource as RestfulResource
from flask_apispec.views import MethodResource


class Resource(MethodResource, RestfulResource):
    pass
