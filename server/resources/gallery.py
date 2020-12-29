from flask_apispec import use_kwargs
from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import fields

from common.schema import GallerySchema
from common.util import ServerError, RequestError
from common.util.decorators import tag, marshal_with
from server.common.database import db
from server.common.database.gallery import Gallery as GalleryModel
from server.common.database.media import Media as MediaModel
from server.common.rest import Resource

__all__ = ['Galleries', 'Gallery']


@tag('gallery')
class Galleries(Resource):
    method_decorators = {'post': [jwt_required]}

    @marshal_with(GallerySchema(many=True), code=200)
    def get(self):
        return GalleryModel.query.all()

    @use_kwargs(GallerySchema)
    @marshal_with(GallerySchema, code=201)
    def post(self, **kwargs):
        gallery = GalleryModel(**kwargs)
        gallery.author = get_current_user()
        try:
            db.session.add(gallery)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return gallery, 201


@tag('gallery')
class Gallery(Resource):
    method_decorators = {'post': [jwt_required], 'put': [jwt_required]}

    @marshal_with(GallerySchema, code=200)
    def get(self, gallery_id):
        return GalleryModel.query.get_or_404(gallery_id)

    @use_kwargs({'media_id': fields.UUID(required=True)})
    @marshal_with(GallerySchema, code=201)
    def post(self, gallery_id, media_id):
        gallery = GalleryModel.query.get_or_404(gallery_id)
        media = MediaModel.query.get_or_404(media_id)
        media_type = media.mimetype.split('/')[0]
        if media_type in ('image', 'video'):
            raise RequestError(f'Media type "{media_type}" is not supported for gallery')
        try:
            gallery.media.append(media)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return gallery, 201

    @use_kwargs(GallerySchema(partial=True))
    @marshal_with(GallerySchema, code=200)
    @marshal_with(GallerySchema, code=201)
    def put(self, gallery_id, **kwargs):
        gallery = GalleryModel.query.get(gallery_id)
        if not gallery:
            try:
                gallery = GalleryModel(**kwargs)
                gallery.author = get_current_user()
                db.session.add(gallery)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
            return gallery, 201
        else:
            gallery.title = kwargs['title']
        return gallery
