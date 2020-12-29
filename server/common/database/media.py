from .mixins import UUIDKeyMixin, UUIDType
from .ref import db


class Media(UUIDKeyMixin, db.Model):
    __tablename__ = 'media'

    name = db.Column(db.String(127), nullable=False)
    mimetype = db.Column(db.String(127), nullable=False)
    extension = db.Column(db.String(15), nullable=False)
    owner_id = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User')

    def get_file_name(self, suffix=''):
        return f'{str(self.id)}{suffix}.{self.extension}'

