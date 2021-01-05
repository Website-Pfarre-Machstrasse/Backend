from marshmallow.fields import Field


class FileField(Field):
    def __init__(self, **additional_metadata):
        additional_metadata.update(location='files')
        super().__init__(**additional_metadata)
