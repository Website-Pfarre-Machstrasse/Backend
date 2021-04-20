import logging


def setup_logging():
    logging.addLevelName(15, 'ACCESS')


def setup_logging_config(app):
    pass
    # from flask import logging as flog
    # log_config = app.config.get_namespace('LOG_')
    # log_config.setdefault('level', logging.DEBUG if app.debug else logging.INFO)
    # log_config.setdefault('style', '{')
    # werkzeug_logger = logging.getLogger('werkzeug')
    # if werkzeug_logger.handlers:
    #     werkzeug_logger.removeHandler(werkzeug_logger.handlers[0])
    # app.logger.removeHandler(flog.default_handler)
    #
    # if 'file' in log_config:
    #     log_config['filename'] = log_config.pop('file')
    #
    # logging.basicConfig(**log_config)
