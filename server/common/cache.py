
__all__ = ['get_app']

from flask import Flask


class AppStore:
    def __init__(self, app=None):
        self.app = app

    def init(self, app_getter):
        self.app = app_getter

    def get_app(self) -> Flask:
        return self.app()


app_store = AppStore()


def get_app():
    app_store.get_app()


def init(app_getter):
    app_store.init(app_getter)
