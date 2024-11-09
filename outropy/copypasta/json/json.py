import json
from typing import Any, Dict, List, Optional, TypeAlias

JSON_OBJECT: TypeAlias = Dict[str, Any]
JSON_ARRAY: TypeAlias = List[Any]
JSON_VAL: TypeAlias = Any


class GenericJSONEncoder(json.JSONEncoder):
    def default(self, obj: object) -> Dict:  # type: ignore
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        else:
            return super().default(obj)  # type: ignore


class InvalidJsonException(Exception):
    def __init__(self, e: Exception, payload: str) -> None:
        self.payload = payload
        self.e = e

    def __str__(self) -> str:
        return f"Invalid JSON {self.e} contents:\n===\n{self.payload[:1000]}\n==="


def dumps(obj: Any) -> str:
    return json.dumps(obj, cls=GenericJSONEncoder)


def loads(json_str: str) -> JSON_OBJECT:
    try:
        return json.loads(json_str)  # type: ignore
    except json.decoder.JSONDecodeError as e:
        raise InvalidJsonException(e, json_str) from e


def try_loads(json_str: str) -> Optional[Any]:
    if json_str is None or json_str == "":
        return None
    try:
        return loads(json_str)
    except json.decoder.JSONDecodeError:
        return None
