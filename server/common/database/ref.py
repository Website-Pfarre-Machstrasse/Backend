from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

db = SQLAlchemy()


def coercion_listener(mapper, class_):
    """
    Auto assigns coercing listener for all class properties which are of coerce
    capable type.
    """
    for prop in mapper.iterate_properties:
        try:
            listener = prop.columns[0].type.coercion_listener
        except AttributeError:
            continue
        event.listen(
            getattr(class_, prop.key),
            'set',
            listener,
            retval=True
        )


event.listen(db.mapper, 'mapper_configured', coercion_listener)
