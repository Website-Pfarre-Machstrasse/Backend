from .ref import jwt
from ..database import User
from ..util import UserNotFoundError

__all__ = []


@jwt.additional_claims_loader
def add_claims_to_access_token(user: User):
    return {'role': user.role.name}


@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.id


@jwt.user_lookup_loader
def user_loader_callback(_jwt_headers, jwt_payload):
    return User.query.get(jwt_payload["sub"])


@jwt.user_lookup_error_loader
def custom_user_loader_error(_jwt_headers, jwt_payload):
    raise UserNotFoundError(jwt_payload["sub"])
