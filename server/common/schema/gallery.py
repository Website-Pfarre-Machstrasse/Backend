from marshmallow import fields

from common.database import Gallery
from common.schema.media import MediaSchema
from common.schema.ref import ma


class GallerySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gallery
        fields = ('id', 'title', 'author', 'media', '_links')
        dump_only = ('id', 'author', 'media', '_links')
        include_relationships = True
        include_fk = True

    author = ma.auto_field(required=False)
    media = fields.Nested(MediaSchema, many=True)
    _links = ma.Hyperlinks({
        'self': ma.URLFor('gallery', values={'gallery_id': '<id>'}),
        'collection': ma.URLFor('galleries')
    })


Gallery.__marshmallow__ = GallerySchema
