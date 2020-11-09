import json
from typing import Any
import uuid


class JSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, uuid.UUID):
            return str(o)
        if hasattr(o, '__json__'):
            return o.__json__()
        return super().default(o)
