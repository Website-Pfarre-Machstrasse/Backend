from flask_jwt_extended import get_current_user, jwt_refresh_token_required, get_jwt_identity, \
    create_access_token, create_refresh_token

from common.schema import UserSchema, LoginSchema, TokenSchema
from common.util.decorators import tag, marshal_with, use_kwargs, jwt_required
from server.common.database.user import User as UserModel
from server.common.rest import Resource

__all__ = ['Self', 'User', 'Users', 'Login', 'Refresh']


@tag('user')
class Self(Resource):
    @jwt_required
    @marshal_with(UserSchema)
    def get(self):
        return get_current_user()


@tag('user')
class User(Resource):
    @jwt_required
    @marshal_with(UserSchema)
    def get(self, user_id):
        return UserModel.query.get_or_404(user_id)


@tag('user')
class Users(Resource):
    @jwt_required
    @marshal_with(UserSchema(many=True))
    def get(self):
        return UserModel.query.all()


@tag('user')
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


@tag('user')
class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    @marshal_with(TokenSchema(only={'access_token'}), code=200)
    def post(self):
        return {
           'access_token': create_access_token(identity=get_jwt_identity())
        }, 200
