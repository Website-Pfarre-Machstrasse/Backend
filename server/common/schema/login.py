from marshmallow import fields

from server.common.schema.ref import ma


class LoginSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
