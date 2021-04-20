import os

from flask import request, send_file
from flask_jwt_extended import get_current_user

from server.common.database import db
from server.common.database.media import Media as MediaModel
from server.common.database.user import Role
from server.common.rest import Resource
from server.common.schema import MediaSchema, FileSchema
from server.common.tinify import tinify
from server.common.util import AuthorisationError, use_kwargs
from server.common.util.decorators import tag, marshal_with, jwt_required, transactional, params
from server.common.util.file import get_save_path

__all__ = ['Medias', 'Media', 'MediaData']


@tag('media')
@params(media_id='The id of the Media')
class MediaData(Resource):

    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='image/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='video/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='audio/*')
    def get(self, media_id):
        """
        ## Get the file for the media with the id media_id
        """
        media = MediaModel.query.get_or_404(media_id)
        mimetype = media.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type == 'image' and 'thumb' in request.args:
            return send_file(os.path.join(save_path, media.get_file_name(suffix='_thumb')), mimetype=media.mimetype)
        return send_file(os.path.join(save_path, media.get_file_name()), mimetype=media.mimetype)


@tag('media')
@params(media_id='The id of the Media')
class Media(Resource):

    @marshal_with(MediaSchema, code=200)
    def get(self, media_id):
        """
        ## Get metadata for the media entry with id media_id
        """
        return MediaModel.query.get_or_404(media_id)

    @jwt_required
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, media_id, _transaction):
        """
        ## Delete the media with id media_id
        ***Requires Authentication***

        You can only edit a media that belongs to you if you are not admin
        """
        media = MediaModel.query.get_or_404(media_id)
        user = get_current_user()
        if media.owner is not user and user.role != Role.admin:
            raise AuthorisationError('You are not allowed to delete this media')

        _transaction.session.delete(media)

        mimetype = media.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type == 'image':
            os.remove(os.path.join(save_path, media.get_file_name(suffix='_thumb')))
        os.remove(os.path.join(save_path, media.get_file_name()))
        return {}, 204


@tag('media')
class Medias(Resource):
    __child__ = Media

    @marshal_with(MediaSchema(many=True), code=200)
    def get(self):
        """
        ## Get the media library
        """
        return MediaModel.query.all()

    @jwt_required
    @use_kwargs(FileSchema, location='files')
    @marshal_with(MediaSchema, code=201)
    @transactional(db.session)
    def post(self, file, _transaction):
        """
        ## Add a new file to the media library
        ***Requires Authentication***
        """
        filename = file.filename.split('.')
        ext = filename[-1]
        name = '.'.join(filename[:-1])
        mimetype = file.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        media = MediaModel(name=name, mimetype=mimetype, extension=ext)
        _transaction.session.add(media)
        _transaction.session.flush()
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
