from .category import Category
from .change import Change
from .event import Event
from .gallery import Gallery
from .media import Media
from .page import Page
from .ref import db
from .user import User

__all__ = ['db', 'User', 'Category', 'Page', 'Change', 'Media', 'Gallery', 'Event', 'setup']


def setup(app):
    db.create_all(app=app)
