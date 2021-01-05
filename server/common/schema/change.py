from marshmallow import fields, validate

from server.common.database import Change
from server.common.schema.ref import ma


class ChangeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Change
        fields = ('category', 'page', 'data', 'created_at', 'author', '_links')
        dump_only = fields
        include_fk = True

    data = fields.List(fields.Tuple((fields.Int(validate=validate.Range(-1, 1)), fields.String)))
    author = fields.UUID()
    _links = ma.Hyperlinks({
        'collection': ma.URLFor('changes', values={'category_id': '<category>', 'page_id': '<page>'}),
        'page': ma.URLFor('page', values={'category_id': '<category>', 'page_id': '<page>'}),
        'author': ma.URLFor('user', values={'user_id': '<author>'})
    })


Change.__marshmallow__ = ChangeSchema
