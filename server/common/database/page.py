from .ref import db


class Page(db.Model):
    __tablename__ = 'page'

    category = db.Column(db.String(20), db.ForeignKey('category.id'), nullable=False, primary_key=True)
    id = db.Column(db.String(20), nullable=False, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(63), nullable=False)
    content = db.relationship("Change")

    @property
    def last_update(self):
        if not self.content:
            return None
        return self.content[-1].created_at
