from flask_jwt_extended import get_current_user

from .mixins import UUIDKeyMixin, UUIDType
from .ref import db

gallery_media_relation = db.Table('gallery_media',
                                  db.Column('media_id', UUIDType, db.ForeignKey('media.id'), primary_key=True),
                                  db.Column('gallery_id', UUIDType, db.ForeignKey('gallery.id'), primary_key=True))


class Gallery(UUIDKeyMixin, db.Model):
    __tablename__ = 'gallery'

    title = db.Column(db.String(63), nullable=False)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), default=lambda: get_current_user().id, nullable=False)
    media = db.relationship('Media', secondary=gallery_media_relation, lazy=True)

