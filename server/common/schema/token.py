from marshmallow import fields

from server.common.schema.ref import ma


class TokenSchema(ma.Schema):
    access_token = fields.String()
    refresh_token = fields.String()
