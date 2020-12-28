from typing import Union

from flask_restx_patched import Api as RestXApi, Namespace

__all__ = ['api']


class Api(RestXApi):
    def get_ns(self, name) -> Union[Namespace, None]:
        for ns in self.namespaces:  # type Namespace
            if ns.name == name:
                return ns
        return None


# authorizations = {
#     'jwtAuth': {
#         'type': 'http',
#         'scheme': 'bearer',
#         'bearerFormat': 'JWT'
#     }
# }
api = Api(prefix='/api',
          # authorizations=authorizations,
          doc=False,
          version='v1',
          title='Pfarre Machstrasse Backend Api',
          validate=True)
