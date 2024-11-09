from typing import Any, List, Type, TypeVar

from pydantic import BaseModel

from outropy.copypasta.json.json import JSON_VAL


def recursive_convert_pydantic_to_dict(data: Any) -> Any:
    if isinstance(data, BaseModel):
        return data.model_dump()
    elif isinstance(data, dict):
        return {
            key: recursive_convert_pydantic_to_dict(value)
            for key, value in data.items()
        }
    elif isinstance(data, list):
        return [recursive_convert_pydantic_to_dict(item) for item in data]
    else:
        return data


T = TypeVar("T", bound=BaseModel)


def to_schema(data: Type[T] | List[Type[T]]) -> JSON_VAL:
    if isinstance(data, list):
        items = []
        for d in data:
            items.append(d.model_json_schema())
        return items
    return data.model_json_schema()
