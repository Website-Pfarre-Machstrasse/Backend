from .ref import db
from ..schemas import ma


class Page(db.Model):
    __tablename__ = 'page'

    category = db.Column(db.String(20), db.ForeignKey('category.id'), nullable=False, primary_key=True)
    id = db.Column(db.String(20), nullable=False, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(63), nullable=False)


class PageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Page
        fields = ('category', 'id', 'title', 'order', '_links')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('page', values={'category_id': '<category>', 'page_id': '<id>'}),
        'collection': ma.URLFor('pages', values={'category_id': '<category>'}),
        'content': ma.URLFor('content', values={'category_id': '<category>', 'page_id': '<id>'})
    })


Page.__marshmallow__ = PageSchema
