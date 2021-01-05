from marshmallow import fields

from server.common.database import Gallery
from server.common.schema.media import MediaSchema
from server.common.schema.ref import ma


class GallerySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gallery
        fields = ('id', 'title', 'owner', 'media', '_links')
        dump_only = ('id', 'owner', 'media', '_links')
        include_relationships = True
        include_fk = True

    id = fields.UUID()
    owner = ma.auto_field('owner_id')
    media = fields.Nested(MediaSchema, many=True)
    _links = ma.Hyperlinks({
        'self': ma.URLFor('gallery', values={'gallery_id': '<id>'}),
        'collection': ma.URLFor('galleries'),
        'owner': ma.URLFor('user', values={'user_id': '<owner>'})
    })


Gallery.__marshmallow__ = GallerySchema
