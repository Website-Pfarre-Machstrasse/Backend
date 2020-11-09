from flask import request
from flask_jwt_extended import jwt_required, get_current_user, jwt_refresh_token_required, get_jwt_identity, \
    create_access_token, create_refresh_token
from flask_restful import Resource

from ..common.database import User as UserModel
from ..common.util import auto_marshall

__all__ = ['User', 'Login', 'Refresh']


class User(Resource):
    method_decorators = [jwt_required, auto_marshall]

    @staticmethod
    def get():
        return get_current_user()


class Login(Resource):
    @staticmethod
    def post():
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        user, auth = UserModel.authenticate(username, password)
        if auth:
            ret = {
                'access_token': create_access_token(identity=user.id),
                'refresh_token': create_refresh_token(identity=user.id)
            }
            return ret, 200
        return {'error': 401, 'message': user}, 401


class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    @staticmethod
    def post():
        current_user = get_jwt_identity()
        ret = {
            'access_token': create_access_token(identity=current_user)
        }
        return ret, 200
