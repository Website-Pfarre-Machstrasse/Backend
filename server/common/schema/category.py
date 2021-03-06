from marshmallow.validate import Range

from server.common.database import Category
from server.common.schema.ref import ma


class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        fields = ('id', 'title', 'order', '_links')
        dump_only = ('_links',)

    order = ma.auto_field(validate=[Range(min=0)])
    _links = ma.Hyperlinks({
        'self': ma.URLFor('category', values={'category_id': '<id>'}),
        'collection': ma.URLFor('categories'),
        'pages': ma.URLFor('pages', values={'category_id': '<id>'})
    })


Category.__marshmallow__ = CategorySchema
