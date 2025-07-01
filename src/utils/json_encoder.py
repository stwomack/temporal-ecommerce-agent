import json
from datetime import datetime
from typing import Any


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


def serialize_for_temporal(obj: Any) -> str:
    """Serialize an object for Temporal, handling datetime objects."""
    return json.dumps(obj, cls=DateTimeEncoder)


def deserialize_from_temporal(data: str) -> Any:
    """Deserialize data from Temporal."""
    return json.loads(data) 