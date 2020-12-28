#!/bin/bash
exec gunicorn --config /server/gunicorn_config.py 'server:create_app()'
