import uuid

from sqlalchemy.dialects.postgresql import UUID

from .ref import db

__all__ = ['UUIDKeyMixin', 'UUIDType', 'TrackUpdateMixin', 'TrackCreationMixin']


class UUIDType(db.TypeDecorator):
    impl = db.CHAR

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(db.CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

    def process_literal_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int


class UUIDKeyMixin:
    @property
    def id(self) -> uuid.UUID:
        return self.__id

    __id = db.Column(UUIDType(), name='id', primary_key=True, default=uuid.uuid4, unique=True, nullable=False)


class TrackCreationMixin:
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())


class TrackUpdateMixin:
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

