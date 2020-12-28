from flask_apispec.views import MethodResource
from flask_restful import Resource as RestfulResource


class Resource(MethodResource, RestfulResource):
    def __init__(self, api):
        self.api = api
