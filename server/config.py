import json
import os

from flask import Flask

from server.common.util import JSONEncoder

parsers = {
    'json': json.load
}


def setup_config(app: Flask):
    testing = os.environ.get('TESTING')
    config_file = os.environ.get('APP_CONFIG')

    if not config_file or not os.path.isfile(config_file):
        if app.debug:
            config_file = 'settings-dev.json'
        elif app.testing or testing:
            config_file = 'settings-test.json'
        else:
            raise ValueError('No config file provided')

    if config_file.endswith('.py'):
        app.config.from_pyfile(config_file)
    else:
        if parser := parsers.get(config_file.split('.')[-1]):
            app.config.from_file(config_file, parser)
        else:
            raise ValueError('Config file is neither json nor python')

    app.config.setdefault('RESTFUL_JSON', {}).setdefault('cls', JSONEncoder)
    app.config.setdefault('APISPEC_FORMAT_RESPONSE', None)
