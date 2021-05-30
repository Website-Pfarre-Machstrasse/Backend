from marshmallow.fields import Field


class FileField(Field):
    def __init__(self, **additional_metadata):
        super().__init__(**additional_metadata, metadata={'location': 'files'})
