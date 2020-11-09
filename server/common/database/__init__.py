from .ref import db
from .user import User
from .media import PageMedia
# from .gallery import Gallery, GalleryMedia


def setup(app):
    db.create_all(app=app)
