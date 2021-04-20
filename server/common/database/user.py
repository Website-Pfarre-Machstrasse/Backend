from server.common.database.mixins import UUIDKeyMixin
from server.common.database.ref import db
from server.common.util import AuthenticationError
from server.common.util.enums import Role
from server.common.util.password import PasswordType


class User(UUIDKeyMixin, db.Model):
    __tablename__ = 'user'
    query: db.Query

    first_name = db.Column(db.String(63), nullable=False)
    last_name = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(127), nullable=False, unique=True)
    password = db.Column(PasswordType, nullable=False)
    role = db.Column(db.Enum(Role), nullable=False, default='author')

    @staticmethod
    def authenticate(username=None, password=None):
        if not username or not password:
            raise AuthenticationError('No credentials provided')

        user: User = User.query.filter_by(email=username).first()

        if not user:
            raise AuthenticationError('User not found')

        if user.password != password:
            raise AuthenticationError('Password incorrect')

        return user
