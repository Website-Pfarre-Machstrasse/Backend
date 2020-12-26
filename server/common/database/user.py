from .ref import db
from .mixins import UUIDKeyMixin
from ..bcrypt import bcrypt
from ..schemas import ma
from ..util import AuthenticationError


class User(UUIDKeyMixin, db.Model):
    __tablename__ = 'user'
    __table_opts__ = {'extend_existing': True}

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
            raise AuthenticationError('User not found')

        if not user.check_password(password):
            raise AuthenticationError('Password incorrect')

        return user


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'role', '_links')

    id = ma.auto_field(column_name='_UUIDKeyMixin__id', dump_only=True)
    password = ma.auto_field(column_name='_User__password', load_only=True, required=False)
    _links = ma.Hyperlinks({
        'self': ma.URLFor('user', values={'user_id': '<id>'}),
        'collection': ma.URLFor('users')
    })


User.__marshmallow__ = UserSchema
