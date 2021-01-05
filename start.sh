#!/bin/bash
exec gunicorn --config ./gunicorn_config.py 'server:create_app()'
