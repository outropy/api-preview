import dataclasses
from typing import Any, Dict

import jsonschema  # type: ignore

from outropy.copypasta.json.json import JSON_OBJECT


@dataclasses.dataclass
class JsonSchema:
    schema_as_json: Dict[str, Any]

    @property
    def schema_id(self) -> str:
        return str(self.schema_as_json.get("$id", ""))

    @property
    def schema_title(self) -> str:
        return str(self.schema_as_json.get("title", ""))

    def _check_valid_schema(self, schema: Dict[str, Any]) -> None:
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f"Invalid schema: {e.message}") from e

    def validate(self, data: Any) -> None:
        try:
            jsonschema.validate(data, self.schema_as_json)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f"Invalid data according to schema: {e.message}") from e


@dataclasses.dataclass
class JsonAndSchema:
    json_schema: JsonSchema
    json_object: JSON_OBJECT
