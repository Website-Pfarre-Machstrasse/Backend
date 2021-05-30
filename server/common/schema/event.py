from marshmallow import fields

from server.common.database import Event
from server.common.schema.ref import ma


class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        fields = ('id', 'name', 'details', 'start', 'end', 'owner', 'media', '_links')
        dump_only = ('id', 'owner', '_links')
        include_fk = True

    id = fields.UUID()
    owner = ma.auto_field('owner_id')
    media = ma.auto_field('media_id')
    _links = ma.Hyperlinks({
        'self': ma.URLFor('event', values={'event_id': '<id>'}),
        'collection': ma.URLFor('events'),
        'owner': ma.URLFor('user', values={'user_id': '<owner>'}),
        'media': ma.URLFor('user', values={'media_id': '<media>'})
    })


Event.__marshmallow__ = EventSchema
