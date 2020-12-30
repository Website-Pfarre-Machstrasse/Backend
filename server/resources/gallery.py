from flask_apispec import use_kwargs
from flask_jwt_extended import jwt_required
from marshmallow import fields

from common.schema import GallerySchema
from common.util import RequestError
from common.util.decorators import tag, marshal_with, transactional
from server.common.database import db
from server.common.database.gallery import Gallery as GalleryModel
from server.common.database.media import Media as MediaModel
from server.common.rest import BasicResource, BasicCollectionResource

__all__ = ['Galleries', 'Gallery']


@tag('gallery')
class Galleries(BasicCollectionResource):
    method_decorators = {'post': [jwt_required]}
    schema = GallerySchema
    model = GalleryModel
    db_session = db.session


@tag('gallery')
class Gallery(BasicResource):
    method_decorators = {'post': [jwt_required], 'put': [jwt_required]}
    schema = GallerySchema
    model = GalleryModel
    db_session = db.session

    @use_kwargs({'media_id': fields.UUID(required=True)})
    @marshal_with(GallerySchema, code=201)
    @transactional(db_session)
    def post(self, gallery_id, media_id):
        gallery = GalleryModel.query.get_or_404(gallery_id)
        media = MediaModel.query.get_or_404(media_id)
        media_type = media.mimetype.split('/')[0]
        if media_type in ('image', 'video'):
            raise RequestError(f'Media type "{media_type}" is not supported for gallery')
        gallery.media.append(media)
        return gallery, 201
