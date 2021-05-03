import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from server.common.bcrypt import bcrypt
from server.common.cors import cors
from server.common.database import setup as setup_db
from server.common.database.ref import db
from server.common.doc import doc
from server.common.jwt.ref import jwt
from server.common.schema.ref import ma, marshmallow_plugin
from server.common.tinify import tinify
from server.config import setup_config
from server.resources.ref import api

__all__ = ['create_app']


def init_extensions(app: Flask):
    db.init_app(app)
    cors.init_app(app, resources=app.config.get('CORS'))
    jwt.init_app(app)
    ma.init_app(app)
    bcrypt.init_app(app)
    tinify.init_app(app)


def create_app():
    from server._logging import setup_logging_config, setup_logging
    setup_logging()
    app = Flask(__name__, static_folder=None, template_folder=None, root_path=os.getcwd())
    setup_config(app)
    setup_logging_config(app)
    init_extensions(app)
    setup_db(app)
    from server.common.util.register import register_resources
    register_resources(api, doc, app, marshmallow_plugin)

    from jwt import InvalidSignatureError

    @app.errorhandler(InvalidSignatureError)
    def handle(e: InvalidSignatureError):
        return e.args[0], 401

    if app.debug:
        from .debug import create_debug_admin
        with app.app_context():
            create_debug_admin()
    else:
        app.wsgi_app = ProxyFix(app.wsgi_app)
    return app
