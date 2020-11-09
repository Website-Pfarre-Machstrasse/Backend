from .ref import db
from .mixins import UUIDKeyMixin, UUIDType


class GalleryMedia(UUIDKeyMixin, db.Model):
    __tablename__ = 'gallery_media'
    __no_marshmallow__ = True

    name = db.Column(db.String(127), nullable=False)
    mimetype = db.Column(db.String(127), nullable=False)
    extension = db.Column(db.String(15), nullable=False)
    gallery_id = db.Column(UUIDType, db.ForeignKey('gallery.id'), nullable=True)

    def get_file_name(self, suffix=''):
        return f'{str(self.id)}{suffix}.{self.extension}'


class Gallery(UUIDKeyMixin, db.Model):
    __tablename__ = 'gallery'

    title = db.Column(db.String(63), nullable=False)
    media = db.relationship('GalleryMedia', backref='gallery', lazy=True)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)
