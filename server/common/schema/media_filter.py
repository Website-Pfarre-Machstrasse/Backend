from marshmallow import fields

from server.common.schema.ref import ma


class MediaFilterSchema(ma.Schema):
    type = fields.String(required=False)
