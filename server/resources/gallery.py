import os

from server.common.database import db
from werkzeug.datastructures import FileStorage
import tinify
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse

from ..common.database.gallery import GalleryMedia, Gallery
from ..common.util.file import get_save_path

__all__ = ['GalleryFiles']

parse = reqparse.RequestParser()
parse.add_argument('file', type=FileStorage, location='files', required=True)


class GalleryFiles(Resource):
    method_decorators = {'post': [jwt_required]}

    @staticmethod
    def post(gallery_id):
        gallery = Gallery.query.get_or_404(gallery_id)
        args = parse.parse_args()
        file: FileStorage = args['file']
        filename = file.filename.split('.')
        ext = filename[-1]
        name = '.'.join(filename[:-1])
        mimetype = file.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type not in ['video', 'image']:
            return {'error': 400, 'message': f'File with type {media_type} is not supported'}, 400
        media = GalleryMedia(name=name, mimetype=mimetype, extension=ext, gallery_id=gallery.id)
        try:
            db.session.add(media)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': 500, 'message': e}, 500
        if media_type == 'image' and tinify.key:
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
