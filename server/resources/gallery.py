import os

from flask import request, send_file
from flask_jwt_extended import jwt_required, get_current_user
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

from ..common.tinify import tinify
from ..common.database import db
from ..common.database.gallery import GalleryMedia as GalleryMediaModel, Gallery as GalleryModel
from ..common.rest import Resource
from ..common.util.file import get_save_path

__all__ = ['Galleries', 'Gallery', 'GalleryMedia']

parse = reqparse.RequestParser()
parse.add_argument('file', type=FileStorage, location='files', required=True)


class Galleries(Resource):
    method_decorators = {'post': [jwt_required]}

    @staticmethod
    def get():
        return GalleryModel.query.all()

    @staticmethod
    def post():
        pass


class Gallery(Resource):
    method_decorators = {'post': [jwt_required], 'put': [jwt_required]}

    @staticmethod
    def get(gallery_id):
        return GalleryModel.query.get_or_404(gallery_id).media

    @staticmethod
    def post(gallery_id):
        gallery = GalleryModel.query.get_or_404(gallery_id)
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
        media = GalleryMediaModel(name=name, mimetype=mimetype, extension=ext, gallery_id=gallery.id)
        try:
            db.session.add(media)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': 500, 'message': e}, 500
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
        return media.id, 201

    @staticmethod
    def put(gallery_id):
        data = GalleryModel.__marshmallow__.load(request.get_json(), partial=True)
        gallery = GalleryModel.query.get(gallery_id)
        if not gallery:
            try:
                gallery = GalleryModel(title=data['title'], author=get_current_user())
                db.session.add(gallery)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return {'error': 500, 'message': e}, 500
        else:
            gallery.title = data['title']
        return gallery


class GalleryMedia(Resource):
    method_decorators = {'delete': [jwt_required]}

    @staticmethod
    def get(media_id):
        media = GalleryMediaModel.query.get_or_404(media_id)
        mimetype = media.mimetype
        media_type = mimetype.split('/')[0]
        save_path = get_save_path(media_type)
        if media_type == 'image' and 'thumb' in request.args:
            return send_file(os.path.join(save_path, media.get_file_name(suffix='_thumb')))
        return send_file(os.path.join(save_path, media.get_file_name()))

    @staticmethod
    def delete(media_id):
        media = GalleryMediaModel.query.get_or_404(media_id)
        try:
            db.session.delete(media)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'error': 500, 'message': e}, 500
        return {}, 204
