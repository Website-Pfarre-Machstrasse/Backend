from .ref import db
from .mixins import UUIDKeyMixin
from ..bcrypt import bcrypt


class User(UUIDKeyMixin, db.Model):
    __tablename__ = 'user'

    def __init__(self, /, first_name: str, last_name: str, email: str, password: str, role: str):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = password
        self.role = role

    def __set_password(self, value: str):
        self.__password = bcrypt.generate_password_hash(value)

    password = property(fset=__set_password)

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
            return 'User no found', False

        if not user.check_password(password):
            return 'Password incorrect', False

        return user, True
