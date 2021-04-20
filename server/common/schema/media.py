from marshmallow import fields

from server.common.database import Media
from server.common.schema.ref import ma


class MediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Media
        fields = ('id', 'name', 'mimetype', 'extension', 'owner', '_links')
        dump_only = ('id', 'owner', '_links')
        include_fk = True

    id = fields.UUID()
    owner = ma.auto_field('owner_id')
    _links = ma.Hyperlinks({
        'self': ma.URLFor('media', values={'media_id': '<id>'}),
        'collection': ma.URLFor('medias'),
        'file': ma.URLFor('media_file', values={'media_id': '<id>'}),
        'thumbnail': ma.URLFor('media_file', values={'media_id': '<id>', 'thumb': ''}),
        'owner': ma.URLFor('user', values={'user_id': '<owner>'})
    })


Media.__marshmallow__ = MediaSchema
