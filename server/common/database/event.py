from flask_jwt_extended import get_current_user

from .mixins import UUIDKeyMixin, UUIDType
from .ref import db


class Event(UUIDKeyMixin, db.Model):
    __tablename__ = 'event'

    name = db.Column(db.String(127), nullable=False)
    details = db.Column(db.String(255), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    owner_id = db.Column(UUIDType, db.ForeignKey('user.id'), default=lambda: get_current_user().id, nullable=False)
    owner = db.relationship('User')
