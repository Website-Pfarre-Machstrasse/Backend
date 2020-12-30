from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from common.bcrypt import bcrypt
from common.cors import cors
from common.database import setup as setup_db
from common.database.ref import db
from common.doc import doc
from common.jwt.ref import jwt
from common.schema.ref import ma, marshmallow_plugin
from common.tinify import tinify
from config import setup_config
from resources.ref import api

__all__ = ['create_app']


def init_extensions(app: Flask):
    db.init_app(app)
    cors.init_app(app, resources=app.config.get('CORS'))
    jwt.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    tinify.init_app(app)


def create_app():
    app = Flask(__name__, static_folder=None, template_folder=None)
    setup_config(app)
    init_extensions(app)
    setup_db(app)
    from common.util.register import register_resources
    register_resources(api, doc, app, marshmallow_plugin)

    if app.debug:
        with app.app_context():
            from debug import create_debug_admin
            create_debug_admin()
    else:
        app.wsgi_app = ProxyFix(app.wsgi_app)
    return app
