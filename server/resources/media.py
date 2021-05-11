import os

from flask import request, send_file
from flask_jwt_extended import get_current_user

from server.common.database import db
from server.common.database.media import Media as MediaModel
from server.common.database.user import Role
from server.common.rest import Resource
from server.common.schema import MediaSchema, MediaFilterSchema
from server.common.schema.file import MediaUploadSchema
from server.common.tinify import tinify
from server.common.util import AuthorisationError, use_kwargs
from server.common.util.decorators import tag, marshal_with, jwt_required, transactional, params
from server.common.util.file import get_save_path

__all__ = ['Medias', 'Media', 'MediaFile']


@tag('media')
@params(media_id='The id of the Media')
class MediaFile(Resource):

    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='image/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='video/*')
    @marshal_with({'type': 'string', 'format': 'binary'}, code=200, content_type='audio/*')
    def get(self, media_id):
        """
        ## Get the file for the media with the id media_id
        """
        media = MediaModel.query.get_or_404(media_id)  # type: MediaModel

        def file_path(media, thumb):
            mimetype = media.mimetype
            media_type = mimetype.split('/')[0]
            suffix = '_thumb' if thumb else ''
            return os.path.join(get_save_path(media_type), media.get_file_name(suffix=suffix))

        thumb = 'thumb' in request.args
        mimetype = 'image/png' if thumb else media.mimetype
        path = file_path(media, thumb)
        return send_file(path,
                         mimetype=mimetype,
                         as_attachment='attachment' in request.args,
                         attachment_filename=f"{media.name}.{media.extension}")


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
        if media_type in {'image', 'video'}:
            os.remove(os.path.join(save_path, media.get_file_name(suffix='_thumb')))
        os.remove(os.path.join(save_path, media.get_file_name()))
        return {}, 204


def create_thumbnail(src, path):
    thumb = src.resize(method="thumb",
                       width=150,
                       height=150)
    thumb.preserve("copyright")
    thumb.to_file(path)


def handle_image_upload(file, save_path, media):
    if tinify.key:
        with file.stream as stream:
            src = tinify.from_buffer(stream.read())
            src.preserve("copyright")
            src.to_file(os.path.join(save_path, media.get_file_name()))
            create_thumbnail(src, os.path.join(save_path, media.get_file_name('_thumb')))
    else:
        file.save(os.path.join(save_path, media.get_file_name()))
        file.save(os.path.join(save_path, media.get_file_name('_thumb')))


def handle_video_upload(file, thumbnail, save_path, media):
    file.save(os.path.join(save_path, media.get_file_name()))
    if thumbnail:
        if tinify.key:
            with thumbnail.stream as stream:
                src = tinify.from_buffer(stream.read())
                create_thumbnail(src, os.path.join(save_path, media.get_file_name('_thumb')))
        else:
            thumbnail.save(os.path.join(save_path, media.get_file_name('_thumb')))


@tag('media')
class Medias(Resource):
    __child__ = Media

    @use_kwargs(MediaFilterSchema, location='query')
    @marshal_with(MediaSchema(many=True), code=200)
    def get(self, type: str = None):
        """
        ## Get the media library
        """
        query = MediaModel.query
        if type:
            query = query.filter(MediaModel.mimetype.startswith(type))
        return query.all()

    @jwt_required
    @use_kwargs(MediaUploadSchema, location='files')
    @marshal_with(MediaSchema, code=201)
    @transactional(db.session)
    def post(self, file, _transaction, thumbnail=None):
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
            handle_image_upload(file, save_path, media)
        elif media_type == 'video':
            handle_video_upload(file, thumbnail, save_path, media)
        else:
            file.save(os.path.join(save_path, media.get_file_name()))
        return media, 201
