#!/bin/bash

pipenv run gunicorn 'server:create_app()'
