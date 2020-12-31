from flask_apispec import use_kwargs

from common.schema import GallerySchema, MediaIdSchema
from common.util import RequestError
from common.util.decorators import tag, marshal_with, transactional, jwt_required, params
from server.common.database import db
from server.common.database.gallery import Gallery as GalleryModel
from server.common.database.media import Media as MediaModel
from server.common.rest import Resource

__all__ = ['Galleries', 'Gallery']


@tag('gallery')
class Galleries(Resource):

    @marshal_with(GallerySchema(many=True), code=200)
    def get(self):
        """
        ## Get all galleries
        """
        return GalleryModel.query.all()

    @jwt_required
    @use_kwargs(GallerySchema)
    @marshal_with(GallerySchema, code=201)
    @transactional(db.session)
    def post(self, _transaction, **kwargs):
        """
        ## Add a new gallery
        ***Requires Authentication***
        """
        gallery = GalleryModel(**kwargs)
        _transaction.session.add(gallery)
        return gallery, 201


@tag('gallery')
@params(gallery_id='The id of the Gallery')
class Gallery(Resource):

    @marshal_with(GallerySchema, code=200)
    def get(self, *args):
        return GalleryModel.query.get_or_404(args)

    @jwt_required
    @use_kwargs(GallerySchema)
    @marshal_with(GallerySchema, code=200)
    @transactional(db.session)
    def put(self, gallery_id, _transaction, **kwargs):
        """
        ## Modify the gallery with the id gallery_id
        ***Requires Authentication***
        """
        obj = GalleryModel.query.get_or_404(gallery_id)
        obj.__dict__.update(**kwargs)
        return obj, 200

    @jwt_required
    @use_kwargs(GallerySchema(partial=True))
    @marshal_with(GallerySchema, code=200)
    @transactional(db.session)
    def patch(self, gallery_id, _transaction, **kwargs):
        """
        ## Modify the gallery with the id gallery_id
        ***Requires Authentication***
        """
        obj = GalleryModel.query.get_or_404(gallery_id)
        obj.__dict__.update(**kwargs)
        return obj, 200

    @jwt_required
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, gallery_id, _transaction):
        """
        ## Delete the gallery with the id gallery_id
        ***Requires Authentication***
        """
        gallery = GalleryModel.query.get_or_404(gallery_id)
        _transaction.session.delete(gallery)
        return {}, 204

    @jwt_required
    @use_kwargs(MediaIdSchema)
    @marshal_with(GallerySchema, code=201)
    @transactional(db.session)
    def post(self, gallery_id, media_id):
        """
        ## Add existing media with id media_id to the gallery with id gallery_id
        ***Requires Authentication***
        """
        gallery = GalleryModel.query.get_or_404(gallery_id)
        media = MediaModel.query.get_or_404(media_id)
        media_type = media.mimetype.split('/')[0]
        if media_type in ('image', 'video'):
            raise RequestError(f'Media type "{media_type}" is not supported for gallery')
        gallery.media.append(media)
        return gallery, 201
