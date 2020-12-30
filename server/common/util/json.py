import uuid
from enum import Enum
from typing import Any

import flask.json


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Enum):
            return o.name
        if hasattr(o, '__json__'):
            return o.__json__()
        return super().default(o)
