import logging
import sys


def setup_logging():
    logging.addLevelName(15, 'ACCESS')


def setup_logging_config(app):
    log_config = app.config.get_namespace('LOG_')
    log_config.setdefault('level', logging.DEBUG if app.debug else logging.INFO)
    log_config.setdefault('style', '{')
    werkzeug_logger = logging.getLogger('werkzeug')
    if werkzeug_logger.handlers:
        werkzeug_logger.removeHandler(werkzeug_logger.handlers[0])
    app.logger.removeHandler(app.logger.handlers[0])

    if 'file' in log_config:
        log_config['filename'] = log_config.pop('file')

    if 'filename' not in log_config:
        log_config['stream'] = sys.stdout

    logging.basicConfig(**log_config)
