from marshmallow import fields

from common.database import Media
from common.schema.ref import ma


class MediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Media
        fields = ('id', 'name', 'mimetype', 'extension', 'owner', '_links')
        dump_only = ('id', 'owner', '_links')
        include_fk = True

    id = fields.UUID()
    _links = ma.Hyperlinks({
        'self': ma.URLFor('media', values={'media_id': '<id>'}),
        'collection': ma.URLFor('medias'),
        'image': ma.URLFor('media_file', values={'media_id': '<id>'}),
        'thumbnail': ma.URLFor('media_file', values={'media_id': '<id>', 'thumb': ''})
    })


Media.__marshmallow__ = MediaSchema
