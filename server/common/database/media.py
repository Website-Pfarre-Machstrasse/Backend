from .ref import db
from .mixins import UUIDKeyMixin


class PageMedia(UUIDKeyMixin, db.Model):
    __tablename__ = 'page_media'
    __no_marshmallow__ = True

    name = db.Column(db.String(127), nullable=False)
    mimetype = db.Column(db.String(127), nullable=False)
    extension = db.Column(db.String(15), nullable=False)

    def get_file_name(self, suffix=''):
        return f'{str(self.id)}{suffix}.{self.extension}'
