import os

from flask import Flask

from common.bcrypt import bcrypt
from common.cors import cors
from common.database import setup as setup_db
from common.database.ref import db
from common.jwt.ref import jwt
from common.schemas.ref import ma
from common.tinify import tinify
from common.util import JSONEncoder
from resources.ref import api

__all__ = ['create_app']


def create_app():
    # region create app
    app = Flask(__name__, static_folder=None)
    # endregion create app
    # region setup config
    config_file = os.environ.get('APP_CONFIG')

    if not config_file or os.path.isfile(config_file):
        if os.environ.get('FLASK_DEBUG') == '1':
            config_file = 'settings-dev.json'
        else:
            raise ValueError('No config file provided')
    app.config.from_json(config_file)
    app.config.setdefault('RESTFUL_JSON', {})
    app.config.get('RESTFUL_JSON').setdefault('cls', JSONEncoder)
    # endregion setup config
    # region init extensions
    db.init_app(app)
    cors.init_app(app, resources=app.config.get('CORS'))
    jwt.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    tinify.init_app(app)
    # endregion init extensions
    # region setup DB
    setup_db(app)
    # event.listen(db.mapper, "after_configured", setup_schema)
    # endregion setup DB
    # region register resources
    from common.util.register import register_resources
    register_resources(api, doc, app)
    # endregion register resources
    # region cache app instance
    # noinspection PyProtectedMember
    from common.cache import init as init_app_store
    init_app_store(db.get_app)
    # endregion cache app instance
    # region add debug admin if debug
    if app.debug:
        with app.app_context():
            from server.common.database.user import User
            # noinspection PyUnresolvedReferences
            if not User.query.filter_by(email="admin@debug.com").first():
                user = User(first_name="Debug",
                            last_name="Admin",
                            email="admin@debug.com",
                            password="AdminPazz69",
                            role="admin")
                db.session.add(user)
                db.session.commit()
    # endregion add debug admin if debug
    # region return app
    return app
    # endregion return app


def setup_schema():
    # noinspection PyProtectedMember,PyUnresolvedReferences
    for class_ in db.Model._decl_class_registry.values():
        if hasattr(class_, "__marshmallow__"):
            continue
        if hasattr(class_, "__tablename__") and not (hasattr(class_, '__no_marshmallow__') and getattr(class_, '__no_marshmallow__')):
            if class_.__name__.endswith("Schema"):
                from marshmallow_sqlalchemy import ModelConversionError
                raise ModelConversionError(
                    "For safety, setup_schema can not be used when a"
                    "Model class ends with 'Schema'"
                )

            if hasattr(class_, '__marshmallow_opts__'):
                meta_dict = {'model': class_, **class_.__marshmallow_opts__}
            else:
                meta_dict = {'model': class_}

            meta_class = type('Meta', (object,), meta_dict)

            schema_class_name = "%sSchema" % class_.__name__

            schema_class = type(schema_class_name, (ma.SQLAlchemyAutoSchema,), {"Meta": meta_class})

            setattr(class_, "__marshmallow__", schema_class)
