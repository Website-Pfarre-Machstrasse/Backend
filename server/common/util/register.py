from ..doc import doc
from server.resources import *


def register_resources():
    register_resource(UserResource, '/user', endpoint='user')
    register_resource(LoginResource, '/login', endpoint='login')
    register_resource(RefreshResource, '/refresh', endpoint='refresh')
    register_resource(GalleriesResource, '/galleries', endpoint='galleries')
    register_resource(GalleryResorce, '/galleries/<uuid:gallery_id>', endpoint='gallery')
    register_resource(GalleryMediaResource, '/gallery_media/<uuid:media_id>', endpoint='gallery_media')


def register_resource(resource_class, *routes, endpoint):
    api.add_resource(resource_class, *routes, endpoint=endpoint)
    doc.register(resource_class, endpoint=endpoint)
