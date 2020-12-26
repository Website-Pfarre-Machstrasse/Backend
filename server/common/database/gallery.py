from marshmallow import fields

from .media import MediaSchema
from .ref import db
from .mixins import UUIDKeyMixin, UUIDType
from ..schemas import ma

gallery_media_relation = db.Table('gallery_media',
                                  db.Column('media_id', UUIDType, db.ForeignKey('media.id'), primary_key=True),
                                  db.Column('gallery_id', UUIDType, db.ForeignKey('gallery.id'), primary_key=True))


class Gallery(UUIDKeyMixin, db.Model):
    __tablename__ = 'gallery'

    title = db.Column(db.String(63), nullable=False)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)
    media = db.relationship('Media', secondary=gallery_media_relation, lazy=True)


class GallerySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Gallery
        fields = ('id', 'title', 'author', 'media', '_links')
        include_relationships = True
        include_fk = True

    id = ma.auto_field(column_name='_UUIDKeyMixin__id', dump_only=True)
    author = ma.auto_field(dump_only=True)
    media = fields.List(fields.Nested(MediaSchema))
    _links = ma.Hyperlinks({
        'self': ma.URLFor('gallery', values={'gallery_id': '<id>'}),
        'collection': ma.URLFor('galleries')
    })


Gallery.__marshmallow__ = GallerySchema
