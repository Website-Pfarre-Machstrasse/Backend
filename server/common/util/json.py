import uuid
from enum import Enum
from typing import Any

import flask.json
from marshmallow import Schema


class JSONEncoder(flask.json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, Enum):
            return o.name
        if isinstance(o, Schema) or issubclass(o, Schema):
            return str(o)
        if hasattr(o, '__json__'):
            return o.__json__()
        return super().default(o)
