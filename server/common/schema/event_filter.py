from marshmallow import fields

from server.common.schema.ref import ma


class EventFilterSchema(ma.Schema):
    start = fields.DateTime(required=False)
    end = fields.DateTime(required=False)
