from common.database import Event
from common.schema.ref import ma


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        fields = ('id', 'name', 'details', 'start', 'end', 'author', '_links')
        dump_only = ('id', 'author', '_links')
        include_fk = True

    _links = ma.Hyperlinks({
        'self': ma.URLFor('event', values={'event_id': '<id>'}),
        'collection': ma.URLFor('events')
    })


Event.__marshmallow__ = EventSchema
