from server.common.database.category import Category
from server.common.database.change import Change
from server.common.database.event import Event
from server.common.database.gallery import Gallery
from server.common.database.media import Media
from server.common.database.page import Page
from server.common.database.ref import db
from server.common.database.user import User

__all__ = ['db', 'User', 'Category', 'Page', 'Change', 'Media', 'Gallery', 'Event', 'setup']


def setup(app):
    db.create_all(app=app)
