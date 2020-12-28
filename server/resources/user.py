from flask_jwt_extended import jwt_required, get_current_user, jwt_refresh_token_required, get_jwt_identity, \
    create_access_token, create_refresh_token
from marshmallow import fields

from common.schemas import ma
from resources.ref import api
from server.common.database.user import User as UserModel
from server.common.rest import Resource

__all__ = ['Self', 'User', 'Users', 'Login', 'Refresh']


class LoginSchema(ma.Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)


class TokenSchema(ma.Schema):
    access_token = fields.String()
    refresh_token = fields.String()


ns = api.get_ns('user')
login_model = ns.model('Login', LoginSchema())
token_model = ns.model('Token', TokenSchema())
token_access_only_model = ns.model('Token(access_token_only)', TokenSchema(only={'access_token'}))
user_model = ns.model('User', UserModel.__marshmallow__())
user_partial_model = ns.model('User(partial)', UserModel.__marshmallow__(partial=True))


class Self(Resource):
    method_decorators = [jwt_required]

    @ns.marshal_with(user_model, code=200)
    def get(self):
        return get_current_user()


class User(Resource):
    method_decorators = [jwt_required]

    @ns.marshal_with(user_model, code=200)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)


class Users(Resource):
    method_decorators = [jwt_required]

    @ns.marshal_with(user_model, code=200, as_list=True)
    def get(self):
        return UserModel.query.all()


class Login(Resource):
    @ns.expect(login_model)
    @ns.marshal_with(token_model, code=200)
    def post(self, **kwargs):
        username = kwargs.get('username', None)
        password = kwargs.get('password', None)
        user = UserModel.authenticate(username, password)
        return {
           'access_token': create_access_token(identity=user),
           'refresh_token': create_refresh_token(identity=user)
        }, 200


class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    @ns.marshal_with(token_access_only_model, code=200)
    def post(self):
        return {
           'access_token': create_access_token(identity=get_jwt_identity())
        }, 200
