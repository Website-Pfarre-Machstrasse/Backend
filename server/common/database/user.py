from .mixins import UUIDKeyMixin
from .ref import db
from ..bcrypt import bcrypt
from ..util import AuthenticationError
from ..util.decorators import write_only_property


class User(UUIDKeyMixin, db.Model):
    __tablename__ = 'user'

    @write_only_property
    def password(self, value: str):
        self.__password = bcrypt.generate_password_hash(value)

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.__password, password)

    first_name = db.Column(db.String(63), nullable=False)
    last_name = db.Column(db.String(63), nullable=False)
    email = db.Column(db.String(127), nullable=False, unique=True)
    __password = db.Column(db.String, name='password', nullable=False)
    role = db.Column(db.Enum('admin', 'author'), nullable=False, default='author')

    @staticmethod
    def authenticate(username, password):
        user: User = User.query.filter_by(email=username).first()

        if not user:
            raise AuthenticationError('User not found')

        if not user.check_password(password):
            raise AuthenticationError('Password incorrect')

        return user
