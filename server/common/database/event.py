from .ref import db
from .mixins import UUIDKeyMixin, UUIDType
from ..schemas import ma


class Event(UUIDKeyMixin, db.Model):
    __tablename__ = 'event'

    name = db.Column(db.String(127), nullable=False)
    details = db.Column(db.String(255), nullable=False)
    start = db.Column(db.DateTime, nullable=False)
    end = db.Column(db.DateTime, nullable=False)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        fields = ('id', 'name', 'details', 'start', 'end', 'author', '_links')
        include_fk = True

    id = ma.auto_field(column_name='_UUIDKeyMixin__id', dump_only=True)
    author = ma.auto_field(dump_only=True)
    _links = ma.Hyperlinks({
        'self': ma.URLFor('event', values={'event_id': '<id>'}),
        'collection': ma.URLFor('events')
    })


Event.__marshmallow__ = EventSchema
