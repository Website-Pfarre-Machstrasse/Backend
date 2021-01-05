from marshmallow import fields

from server.common.schema.ref import ma


class MediaIdSchema(ma.Schema):
    media_id = fields.UUID(required=True)
