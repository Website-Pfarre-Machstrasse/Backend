from .ref import db
from .mixins import UUIDKeyMixin, UUIDType


class Event(UUIDKeyMixin, db.Model):
    __tablename__ = 'event'
    __no_marshmallow__ = True

    name = db.Column(db.String(127), nullable=False)
    details = db.Column(db.String(255), nullable=False)
    start = db.Column(db.TIMESTAMP, nullable=False)
    end = db.Column(db.TIMESTAMP, nullable=False)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)


