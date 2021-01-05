from marshmallow.validate import Range

from server.common.database import Page
from server.common.schema.ref import ma


class PageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Page
        fields = ('category', 'id', 'title', 'order', '_links')
        dump_only = ('_links',)
        include_fk = True

    order = ma.auto_field(validate=[Range(min=0)])
    _links = ma.Hyperlinks({
        'self': ma.URLFor('page', values={'category_id': '<category>', 'page_id': '<id>'}),
        'collection': ma.URLFor('pages', values={'category_id': '<category>'}),
        'content': ma.URLFor('content', values={'category_id': '<category>', 'page_id': '<id>'})
    })


Page.__marshmallow__ = PageSchema
