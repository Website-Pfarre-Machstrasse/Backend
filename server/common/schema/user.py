from marshmallow import fields

from common.database.user import User
from common.schema.ref import ma, ModelConverter


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        model_converter = ModelConverter
        fields = ('id', 'password', 'first_name', 'last_name', 'email', 'role', '_links')
        dump_only = ('id', '_links')
        load_only = ('password',)

    id = fields.UUID()
    password = fields.String()
    _links = ma.Hyperlinks({
        'self': ma.URLFor('user', values={'user_id': '<id>'}),
        'collection': ma.URLFor('users')
    })


User.__marshmallow__ = UserSchema
