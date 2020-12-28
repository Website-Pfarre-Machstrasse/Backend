from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import fields

from common.util import ServerError, RequestError
from resources.ref import api
from server.common.database import db
from server.common.database.gallery import Gallery as GalleryModel
from server.common.database.media import Media as MediaModel
from server.common.rest import Resource

__all__ = ['Galleries', 'Gallery']

ns = api.get_ns('gallery')
gallery_model = ns.model('Gallery', GalleryModel.__marshmallow__())
gallery_partial_model = ns.model('Gallery(partial)', GalleryModel.__marshmallow__(partial=True))


class Galleries(Resource):
    method_decorators = {'post': [jwt_required]}

    @ns.marshal_with(gallery_model, code=200, as_list=True)
    def get(self):
        return GalleryModel.query.all()

    @ns.expect(gallery_model)
    @ns.marshal_with(gallery_model, code=201)
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


class Gallery(Resource):
    method_decorators = {'post': [jwt_required], 'put': [jwt_required]}

    @ns.marshal_with(gallery_model, code=200)
    def get(self, gallery_id):
        return GalleryModel.query.get_or_404(gallery_id)

    @ns.expect({'media_id': fields.UUID})
    @ns.marshal_with(gallery_model, code=201)
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

    @ns.expect(gallery_model)
    @ns.marshal_with(gallery_model, code=200)
    @ns.marshal_with(gallery_model, code=201)
    def put(self, gallery_id, **kwargs):
        gallery = GalleryModel.query.get(gallery_id)
        if not gallery:
            gallery = GalleryModel(title=kwargs['title'], author=get_current_user())
            try:
                db.session.add(gallery)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
            return gallery, 201
        else:
            try:
                gallery.title = kwargs['title']
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                raise ServerError(e)
            return gallery
