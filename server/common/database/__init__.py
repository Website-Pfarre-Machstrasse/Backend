from .ref import db
from .user import User
from .category import Category
from .page import Page
from .change import Change
from .media import Media
from .gallery import Gallery
from .event import Event

Category.pages = db.relationship("Page")
Page.content = db.relationship("Change")


def setup(app):
    db.create_all(app=app)
