from .ref import db
from .mixins import UUIDType


class Change(db.Model):
    __tablename__ = 'change'
    __table_args__ = (db.ForeignKeyConstraint(('category', 'page'), ('page.category', 'page.id')),)

    category = db.Column(db.String(20), nullable=False, primary_key=True)
    page = db.Column(db.String(20), nullable=False, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp(), primary_key=True)
    data = db.Column(db.JSON, nullable=False)
    author = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)
