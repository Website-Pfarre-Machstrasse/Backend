from .ref import db


class Category(db.Model):
    __tablename__ = 'category'
    __no_marshmallow__ = True

    id = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    order = db.Column(db.INTEGER, nullable=False)
    name = db.Column(db.String(127), nullable=False)
    pages = db.relationship("Page")


