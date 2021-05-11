from flask import current_app
from marshmallow import validates, ValidationError
from werkzeug.datastructures import FileStorage

from server.common.schema.ref import ma, FileField


def validate_media_file(file: FileStorage, /, allowed: list = None, app=None, config: dict = None) -> None:
    if not allowed:
        if not config:
            if not app:
                app = current_app
            config = app.config
        allowed = config.get('ALLOWED_MEDIA_TYPES', [])

    mimetype = file.mimetype
    media_type = mimetype.split('/')[0]
    if media_type not in allowed and mimetype not in allowed:
        raise ValidationError(f'File with type {media_type} is not supported')


class FileSchema(ma.Schema):
    file = FileField(required=True)

    @validates('file')
    def validate_file(self, file: FileStorage):
        validate_media_file(file)


class MediaUploadSchema(ma.Schema):
    file = FileField(required=True)
    thumbnail = FileField(required=False)

    @validates('file')
    def validate_file(self, file: FileStorage):
        validate_media_file(file)

    @validates('thumbnail')
    def validate_thumbnail(self, thumbnail: FileStorage):
        validate_media_file(thumbnail, allowed=['image'])
