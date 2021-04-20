from flask_jwt_extended import get_current_user

from server.common.database.mixins import UUIDKeyMixin, UUIDType
from server.common.database.ref import db


class Event(UUIDKeyMixin, db.Model):
    __tablename__ = 'event'
    query: db.Query

    name = db.Column(db.String(127), nullable=False)
    details = db.Column(db.String(255), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    media_id = db.Column(UUIDType, db.ForeignKey('media.id'), nullable=True)
    media = db.relationship('Media')
    owner_id = db.Column(UUIDType, db.ForeignKey('user.id'), default=lambda: get_current_user().id, nullable=False)
    owner = db.relationship('User')
