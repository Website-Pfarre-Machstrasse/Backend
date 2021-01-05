from marshmallow import validates, ValidationError
from werkzeug.datastructures import FileStorage

from server.common.schema.ref import ma, FileField


class FileSchema(ma.Schema):
    file = FileField(required=True)

    @validates('file')
    def validate_media_file(self, file: FileStorage):
        mimetype = file.mimetype
        media_type = mimetype.split('/')[0]
        if media_type not in ['video', 'image', 'audio']:
            raise ValidationError(f'File with type {media_type} is not supported')
