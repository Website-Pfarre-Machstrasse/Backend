

def register_resources(api):
    # region namespaces
    user_ns = api.namespace('user', path='/')
    gallery_ns = api.namespace('gallery')
    content_ns = api.namespace('content', path='/category')
    media_ns = api.namespace('media')
    event_ns = api.namespace('event')
    # endregion
    # region import
    from server.resources import (
        SelfResource,
        LoginResource,
        RefreshResource,
        UserResource,
        UsersResource,
        GalleriesResource,
        GalleryResource,
        CategoriesResource,
        CategoryResource,
        PagesResource,
        PageResource,
        PageContentResource,
        MediasResource,
        MediaResource,
        MediaDataResource,
        EventsResource,
        EventResource
    )
    # endregion
    # region user
    user_ns.add_resource(SelfResource, '/self', endpoint='self')
    user_ns.add_resource(LoginResource, '/login', endpoint='login')
    user_ns.add_resource(RefreshResource, '/refresh', endpoint='refresh')
    user_ns.add_resource(UserResource, '/user', endpoint='users')
    user_ns.add_resource(UsersResource, '/user/<uuid:user_id>', endpoint='user')
    # endregion
    # region gallery
    gallery_ns.add_resource(GalleriesResource, '/', endpoint='galleries')
    gallery_ns.add_resource(GalleryResource, '/<uuid:gallery_id>', endpoint='gallery')
    # endregion
    # region content
    content_ns.add_resource(CategoriesResource, '/', endpoint='categories')
    content_ns.add_resource(CategoryResource, '/<string:category_id>', endpoint='category')
    content_ns.add_resource(PagesResource, '/<string:category_id>/page', endpoint='pages')
    content_ns.add_resource(PageResource, '/<string:category_id>/page/<string:page_id>', endpoint='page')
    content_ns.add_resource(PageContentResource, '/<string:category_id>/page/<string:page_id>/content', endpoint='content')
    # endregion
    # region media
    media_ns.add_resource(MediasResource, '/', endpoint='medias')
    media_ns.add_resource(MediaResource, '/<uuid:media_id>', endpoint='media')
    media_ns.add_resource(MediaDataResource, '/media/<uuid:media_id>/file', endpoint='media_file')
    # endregion
    # region event
    event_ns.add_resource(EventsResource, '/', endpoint='events')
    event_ns.add_resource(EventResource, '/<uuid:event_id>', endpoint='event')
    # endregion
