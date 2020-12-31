from marshmallow import fields

from common.schema import ma


class MediaIdSchema(ma.Schema):
    media_id = fields.UUID(required=True)
