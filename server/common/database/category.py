from .ref import db
from ..schemas import ma


class Category(db.Model):
    __tablename__ = 'category'

    id = db.Column(db.String(20), unique=True, nullable=False, primary_key=True)
    order = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(127), nullable=False)


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        fields = ('id', 'title', 'order', '_links')

    _links = ma.Hyperlinks({
        'self': ma.URLFor('category', values={'category_id': '<id>'}),
        'collection': ma.URLFor('categories'),
        'pages': ma.URLFor('pages', values={'category_id': '<id>'})
    })


Category.__marshmallow__ = CategorySchema
