from flask_jwt_extended import get_current_user

from server.common.database.mixins import UUIDType
from server.common.database.ref import db


class Change(db.Model):
    __tablename__ = 'change'
    __table_args__ = (db.ForeignKeyConstraint(('category', 'page'), ('page.category', 'page.id')),)
    query: db.Query

    category = db.Column(db.String(20), nullable=False, primary_key=True)
    page = db.Column(db.String(20), nullable=False, primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), primary_key=True)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), default=lambda: get_current_user().id, nullable=False)
