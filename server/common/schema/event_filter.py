from marshmallow import fields

from common.schema import ma


class EventFilterSchema(ma.Schema):
    start = fields.DateTime(required=False)
    end = fields.DateTime(required=False)
