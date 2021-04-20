from server.common.database.ref import db


class Category(db.Model):
    __tablename__ = 'category'
    query: db.Query

    id = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(127), nullable=False)
    pages = db.relationship("Page")
