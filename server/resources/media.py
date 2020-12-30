import os

from flask import request, send_file
from flask_jwt_extended import get_current_user
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

from common.schema import MediaSchema
from common.tinify import tinify
from common.util import AuthorisationError, ServerError, RequestError
from common.util.decorators import tag, marshal_with, jwt_required
from server.common.database import db
from server.common.database.media import Media as MediaModel
from server.common.rest import Resource
from server.common.util.file import get_save_path

__all__ = ['Medias', 'Media', 'MediaData']

parse = reqparse.RequestParser()
parse.add_argument('file', type=FileStorage, location='files', required=True)


@tag('media')
class Medias(Resource):

    @marshal_with(MediaSchema(many=True), code=200)
    def get(self):
        return MediaModel.query.all()

    @jwt_required
    @marshal_with(MediaSchema, code=201)
    def post(self):
        args = parse.parse_args()
        file: FileStorage = args['file']
        filename = file.filename.split('.')
        ext = filename[-1]
        name = '.'.join(filename[:-1])
        mimetype = file.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type not in ['video', 'image', 'audio']:
            raise RequestError(f'File with type {media_type} is not supported')
        media = MediaModel(name=name, mimetype=mimetype, extension=ext)
        media.owner_id = get_current_user().id
        try:
            db.session.add(media)
            db.session.commit()
            if media_type == 'image':
                if tinify.key:
                    with file.stream as stream:
                        src = tinify.from_buffer(stream.read())
                        src.preserve("copyright")
                        src.to_file(os.path.join(save_path, media.get_file_name()))
                        thumb = src.resize(method="thumb",
                                           width=150,
                                           height=150)
                        thumb.preserve("copyright")
                        thumb.to_file(os.path.join(save_path, media.get_file_name('_thumb')))
                else:
                    file.save(os.path.join(save_path, media.get_file_name()))
            else:
                file.save(os.path.join(save_path, media.get_file_name()))
            return media, 201
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)


@tag('media')
class Media(Resource):

    @marshal_with(MediaSchema, code=200)
    def get(self, media_id):
        return MediaModel.query.get_or_404(media_id)

    @jwt_required
    @marshal_with(None, code=204)
    def delete(self, media_id):
        media = MediaModel.query.get_or_404(media_id)
        user = get_current_user()
        if media.owner is not user and user.role != 'admin':
            raise AuthorisationError('You are not allowed to delete this media')
        try:
            db.session.delete(media)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204


@tag('media')
class MediaData(Resource):

    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='image/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='video/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='audio/*')
    def get(self, media_id):
        media = MediaModel.query.get_or_404(media_id)
        mimetype = media.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type == 'image' and 'thumb' in request.args:
            return send_file(os.path.join(save_path, media.get_file_name(suffix='_thumb')), mimetype=media.mimetype)
        return send_file(os.path.join(save_path, media.get_file_name()), mimetype=media.mimetype)
