from .ref import db


class Page(db.Model):
    __tablename__ = 'page'
    __no_marshmallow__ = True

    id = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    order = db.Column(db.INTEGER, nullable=False)
    title = db.Column(db.String(63), nullable=False)
    content = db.relationship("Change")
    category = db.Column(db.String(20), db.ForeignKey('category.id'), nullable=False)


