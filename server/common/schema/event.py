from marshmallow import fields

from server.common.database import Event
from server.common.schema.ref import ma


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        fields = ('id', 'name', 'details', 'start', 'end', 'owner', '_links')
        dump_only = ('id', 'owner', '_links')
        include_fk = True

    id = fields.UUID()
    owner = ma.auto_field('owner_id')
    _links = ma.Hyperlinks({
        'self': ma.URLFor('event', values={'event_id': '<id>'}),
        'collection': ma.URLFor('events'),
        'owner': ma.URLFor('user', values={'user_id': '<owner>'})
    })


Event.__marshmallow__ = EventSchema
