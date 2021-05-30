from logging import Logger, root as root_logger

from flask_apispec.views import MethodResource
from flask_restful import Resource as RestfulResource

from server.common.util.decorators import autodoc


class Resource(MethodResource, RestfulResource):
    def __init__(self, *args, **kwargs):
        super(Resource, self).__init__(*args, **kwargs)
        self.logger = Logger(f'{type(self).__name__}Resource', root_logger.level)
        self.logger.parent = root_logger

    def __init_subclass__(cls, **kwargs):
        return autodoc(cls)
