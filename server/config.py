import logging
import os

from flask import Flask

from server.common.util import JSONEncoder


def setup_config(app: Flask):
    config_file = os.environ.get('APP_CONFIG')

    if not config_file or os.path.isfile(config_file):
        if app.debug:
            config_file = 'settings-dev.json'
        else:
            raise ValueError('No config file provided')

    if config_file.endswith('.json'):
        app.config.from_json(config_file)
    elif config_file.endswith('.py'):
        app.config.from_pyfile(config_file)
    else:
        raise ValueError('Config file is neither json nor python')

    app.config.setdefault('RESTFUL_JSON', {}).setdefault('cls', JSONEncoder)
    app.config.setdefault('APISPEC_FORMAT_RESPONSE', None)
    logging.basicConfig(level=app.config.get('LOG_LEVEL', logging.DEBUG if app.debug else logging.INFO))
