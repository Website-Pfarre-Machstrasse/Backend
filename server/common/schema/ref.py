from flask_marshmallow import Marshmallow

__all__ = ['ma', 'ModelConverter', 'marshmallow_plugin', 'FileField', 'enum2properties', 'tuple2properties']

from .custom_fields import FileField
from .customizations import MarshmallowPlugin, resolver, ModelConverter, enum2properties, tuple2properties

ma = Marshmallow()
marshmallow_plugin = MarshmallowPlugin(resolver)
