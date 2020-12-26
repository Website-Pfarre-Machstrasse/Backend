import errno
import os

from ..database import db


def get_save_path(media_type):
    store_path = os.path.abspath(os.path.normpath(db.get_app().config.get("FILE_STORE", None)))
    if not store_path:
        store_path = os.path.join(db.get_app().instance_path, 'files')
    path = os.path.join(store_path, media_type)
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    return path
