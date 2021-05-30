from .ref import jwt
from ..database import User
from ..util import UserNotFoundError
from flask_jwt_extended.config import config as jwt_config

__all__ = []


@jwt.additional_claims_loader
def add_claims_to_access_token(user):
    return {'role': user.role.name}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id if isinstance(user, User) else user


@jwt.user_lookup_loader
def user_loader_callback(header, payload):
    return User.query.get(payload.get(jwt_config.identity_claim_key))


@jwt.user_lookup_error_loader
def custom_user_loader_error(header, payload):
    raise UserNotFoundError(payload.get(jwt_config.identity_claim_key))
