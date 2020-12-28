from .mixins import UUIDKeyMixin, UUIDType
from .ref import db
from ..schemas import ma


class Media(UUIDKeyMixin, db.Model):
    __tablename__ = 'media'

    name = db.Column(db.String(127), nullable=False)
    mimetype = db.Column(db.String(127), nullable=False)
    extension = db.Column(db.String(15), nullable=False)
    owner_id = db.Column(UUIDType, db.ForeignKey('user.id'), nullable=False)
    owner = db.relationship('User')

    def get_file_name(self, suffix=''):
        return f'{str(self.id)}{suffix}.{self.extension}'


class MediaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Media
        fields = ('id', 'name', 'mimetype', 'extension', 'owner', '_links')
        dump_only = ('id', 'owner', '_links')
        include_fk = True

    owner = ma.auto_field(column_name='owner_id', dump_only=True)
    _links = ma.Hyperlinks({
        'self': ma.URLFor('media', values={'media_id': '<id>'}),
        'collection': ma.URLFor('medias'),
        'image': ma.URLFor('media_file', values={'media_id': '<id>'}),
        'thumbnail': ma.URLFor('media_file', values={'media_id': '<id>', 'thumb': ''})
    })


Media.__marshmallow__ = MediaSchema
