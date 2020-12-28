from flask_apispec import marshal_with, use_kwargs, doc
from flask_jwt_extended import jwt_required, get_current_user, jwt_refresh_token_required, get_jwt_identity, \
    create_access_token, create_refresh_token
from marshmallow import fields

from common.schemas import ma
from server.common.database.user import User as UserModel
from server.common.rest import Resource

__all__ = ['Self', 'User', 'Users', 'Login', 'Refresh']


class LoginSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class TokenSchema(ma.Schema):
    access_token = fields.String()
    refresh_token = fields.String()


def auth_required(fn):
    return doc()(fn)


@doc(tags=['user'], params={
    'Authorization': {
        'description':
            'Authorization HTTP header with JWT access token, like: Authorization: Bearer asdf.qwer.zxcv',
        'in':
            'header',
        'type':
            'string',
        'required':
            True
    }
})
class Self(Resource):
    method_decorators = [jwt_required]

    @marshal_with(UserModel.__marshmallow__)
    def get(self):
        return get_current_user()


@doc(tags=['user'])
class User(Resource):
    method_decorators = [jwt_required]

    @marshal_with(UserModel.__marshmallow__)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)


@doc(tags=['user'])
class Users(Resource):
    method_decorators = [jwt_required]

    @marshal_with(UserModel.__marshmallow__(many=True))
    def get(self):
        return UserModel.query.all()


@doc(tags=['user'])
class Login(Resource):
    @use_kwargs(LoginSchema)
    @marshal_with(TokenSchema, code=200)
    def post(self, **kwargs):
        username = kwargs.get('username', None)
        password = kwargs.get('password', None)
        user = UserModel.authenticate(username, password)
        return {
           'access_token': create_access_token(identity=user),
           'refresh_token': create_refresh_token(identity=user)
        }, 200


@doc(tags=['user'])
class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    @marshal_with(TokenSchema(only={'access_token'}), code=200)
    def post(self):
        return {
           'access_token': create_access_token(identity=get_jwt_identity())
        }, 200
