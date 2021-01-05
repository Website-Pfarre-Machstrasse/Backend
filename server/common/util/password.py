from sqlalchemy import types
from sqlalchemy.dialects import oracle, postgresql, sqlite, mysql
from sqlalchemy.ext.mutable import Mutable

from ..bcrypt import bcrypt


class Password(Mutable, object):

    @classmethod
    def coerce(cls, key, value):
        if isinstance(value, Password):
            return value

        if isinstance(value, (str, bytes)):
            return cls(value, secret=True)

        super(Password, cls).coerce(key, value)

    def __init__(self, value, secret=False):
        if secret:
            self.hash = None
            self.secret = value
        else:
            if isinstance(value, str):
                value = value.encode('utf8')
            self.hash = value
            self.secret = None

    def __eq__(self, value):
        if value is None or self.hash is None:
            return self.hash is value

        if isinstance(value, Password):
            return value.hash == self.hash

        if isinstance(value, (str, bytes)):
            return bcrypt.check_password_hash(self.hash, value)

        return False

    def __ne__(self, value):
        return not (self == value)


class PasswordType(types.TypeDecorator):

    impl = types.BINARY(60)
    python_type = Password

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_rounds = kwargs.pop('encryption_rounds', None)

    def process_literal_param(self, value, dialect):
        return self.process_value(value)

    def process_bind_param(self, value, dialect):
        return self.process_value(value)

    def process_value(self, value):
        if isinstance(value, Password):
            if value.secret is not None:
                value.hash = self._hash(value.secret)
                value.secret = None
            return value.hash

        if isinstance(value, str):
            return self._hash(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return Password(value)

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            # Use a BYTEA type for postgresql.
            impl = postgresql.BYTEA(60)
        elif dialect.name == 'oracle':
            # Use a RAW type for oracle.
            impl = oracle.RAW(60)
        elif dialect.name == 'sqlite':
            # Use a BLOB type for sqlite
            impl = sqlite.BLOB(60)
        elif dialect.name == 'mysql':
            # Use a BINARY type for mysql.
            impl = mysql.BINARY(60)
        else:
            impl = types.VARBINARY(60)
        return dialect.type_descriptor(impl)

    def _hash(self, value) -> bytes:
        return bcrypt.generate_password_hash(value, self.encryption_rounds)

    def coercion_listener(self, target, value, oldvalue, initiator):
        if value is None:
            return

        if not isinstance(value, Password):
            value = self._hash(value)
            return Password(value)
        else:
            if value.secret is not None:
                value.hash = self._hash(value.secret)
                value.secret = None

        return value

    @property
    def python_type(self):
        return self.impl.type.python_type


Password.associate_with(PasswordType)
