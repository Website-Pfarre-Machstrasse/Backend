from flask_jwt_extended import get_current_user

from server.common.database.mixins import UUIDKeyMixin, UUIDType
from server.common.database.ref import db


class Media(UUIDKeyMixin, db.Model):
    __tablename__ = 'media'
    query: db.Query

    name = db.Column(db.String(127), nullable=False)
    mimetype = db.Column(db.String(127), nullable=False)
    extension = db.Column(db.String(15), nullable=False)
    owner_id = db.Column(UUIDType, db.ForeignKey('user.id'), default=lambda: get_current_user().id, nullable=False)
    owner = db.relationship('User')

    def get_file_name(self, suffix=''):
        return f'{str(self.id)}{suffix}.{self.extension}'

