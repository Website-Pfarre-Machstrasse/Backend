from flask_jwt_extended import (
    get_current_user, jwt_refresh_token_required, create_access_token, create_refresh_token
)

from server.common.database import User as UserModel
from server.common.database import db
from server.common.rest import Resource
from server.common.schema import UserSchema, LoginSchema, TokenSchema
from server.common.util import AuthorisationError
from server.common.util.decorators import (
    tag, marshal_with, use_kwargs, jwt_required, admin_required, transactional, params, op_id
)
from server.common.util.enums import Role

__all__ = ['Self', 'User', 'Users', 'Login', 'Refresh']


@tag('user')
class Self(Resource):

    @op_id('self')
    @jwt_required
    @marshal_with(UserSchema, code=200)
    def get(self):
        """
        ## Get the currently authenticated user
        ***Requires Authentication***
        """
        return get_current_user()


@tag('user')
@params(user_id='The id of the User')
class User(Resource):

    @marshal_with(UserSchema, code=200)
    def get(self, user_id):
        """
        ## Get user by id
        """
        return UserModel.query.get_or_404(user_id)

    @jwt_required
    @use_kwargs(UserSchema(partial=True))
    @marshal_with(UserSchema, code=200)
    @transactional(db.session)
    def patch(self, user_id, _transaction, **kwargs):
        """
        ## Modify user with id user_id
        ***Requires Authentication***

        You can only edit yourself if you are not admin
        """
        user = UserModel.query.get_or_404(user_id)
        current = get_current_user()
        if user is not current and current.role != Role.admin:
            raise AuthorisationError('You are not allowed to modify this user')
        if 'password' in kwargs and kwargs['password'] != user.password:
            pass  # TODO
        for k, v in kwargs.items():
            setattr(user, k, v)
        return user

    @jwt_required
    @use_kwargs(UserSchema)
    @marshal_with(UserSchema, code=200)
    @transactional(db.session)
    def put(self, user_id, _transaction, **kwargs):
        """
        ## Modify user with id user_id
        ***Requires Authentication***

        You can only edit yourself if you are not admin
        """
        user = UserModel.query.get_or_404(user_id)
        current = get_current_user()
        if user.id != get_current_user().id and current.role is not Role.admin:
            raise AuthorisationError('You are not allowed to modify this user')
        if kwargs['password'] != user.password:
            pass  # TODO
        for k, v in kwargs.items():
            setattr(user, k, v)
        return user

    @admin_required
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, user_id, _transaction):
        """
        ## Delete the user with id user_id
        ***Requires administrator rights***
        """
        user = UserModel.query.get_or_404(user_id)
        _transaction.session.delete(user)
        return {}, 204


@tag('user')
class Users(Resource):
    __child__ = User

    @jwt_required
    @marshal_with(UserSchema(many=True))
    def get(self):
        """
        ## Get all users
        ***Requires Authentication***
        """
        return UserModel.query.all()

    @admin_required
    @use_kwargs(UserSchema)
    @marshal_with(UserSchema, code=201)
    @transactional(db.session)
    def post(self, _transaction, **kwargs):
        """
        ## Create a new user
        ***Requires administrator rights***
        """
        user = UserModel(**kwargs)
        _transaction.session.add(user)
        return user, 201


@tag('user')
class Login(Resource):

    @op_id('login')
    @use_kwargs(LoginSchema, location='json_or_form')
    @marshal_with(TokenSchema, code=200)
    def post(self, **kwargs):
        """
        ## Login a user with the given username and password located in the json request or the form
        """
        user = UserModel.authenticate(**kwargs)
        return {
           'access_token': create_access_token(identity=user),
           'refresh_token': create_refresh_token(identity=user)
        }, 200


@tag('user')
class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    @op_id('refresh')
    @marshal_with(TokenSchema(only={'access_token'}), code=200)
    def post(self):
        """
        ## Request a new access_token for the current refresh_token in the Authorisation header
        """
        return {
           'access_token': create_access_token(identity=get_current_user())
        }, 200
