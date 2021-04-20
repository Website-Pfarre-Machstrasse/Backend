from .ref import jwt
from ..database import User
from ..util import UserNotFoundError

__all__ = []


@jwt.user_claims_loader
def add_claims_to_access_token(user):
    return {'role': user.role.name}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id if isinstance(user, User) else user


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    return User.query.get(identity)


@jwt.user_loader_error_loader
def custom_user_loader_error(identity):
    raise UserNotFoundError(identity)
