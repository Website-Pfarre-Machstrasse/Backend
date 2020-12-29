from flask import Flask

from server.resources import *

registered = False


def register_resources(api, doc, app: Flask):
    global registered
    if registered:
        return

    def register_resource(resource_class, *routes, endpoint):
        api.add_resource(resource_class, *routes, endpoint=endpoint)
        doc.register(resource_class, endpoint=endpoint)

    register_resource(SelfResource, '/self', endpoint='self')
    register_resource(UserResource, '/user', endpoint='users')
    register_resource(UsersResource, '/user/<uuid:user_id>', endpoint='user')
    register_resource(LoginResource, '/login', endpoint='login')
    register_resource(RefreshResource, '/refresh', endpoint='refresh')
    register_resource(GalleriesResource, '/galleries', endpoint='galleries')
    register_resource(GalleryResource, '/galleries/<uuid:gallery_id>', endpoint='gallery')
    register_resource(CategoriesResource, '/category', endpoint='categories')
    register_resource(CategoryResource, '/category/<string:category_id>', endpoint='category')
    register_resource(PagesResource, '/category/<string:category_id>/page', endpoint='pages')
    register_resource(PageResource, '/category/<string:category_id>/page/<string:page_id>', endpoint='page')
    register_resource(PageContentResource, '/category/<string:category_id>/page/<string:page_id>/content', endpoint='content')
    register_resource(MediasResource, '/media', endpoint='medias')
    register_resource(MediaResource, '/media/<uuid:media_id>', endpoint='media')
    register_resource(MediaDataResource, '/media/<uuid:media_id>/file', endpoint='media_file')
    register_resource(EventsResource, '/event', endpoint='events')
    register_resource(EventResource, '/event/<uuid:event_id>', endpoint='event')

    api.init_app(app)
    api.app = app
    app.extensions['restful'] = api
    doc.init_app(app)

    registered = True
