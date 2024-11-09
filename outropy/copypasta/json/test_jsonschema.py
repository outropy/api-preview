import unittest

from outropy.copypasta.json.jsonschema import JsonSchema


class TestJsonSchema(unittest.TestCase):
    def test_validates_object_according_to_schema(self) -> None:
        valid_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
            "required": ["name", "age"],
        }

        s = JsonSchema(valid_schema)

        valid_obj = {"name": "Alice", "age": 42}
        s.validate(valid_obj)  # This should pass without exception

        invalid_obj = {"name": "Alice", "age": "42"}
        with self.assertRaises(ValueError):
            s.validate(invalid_obj)

    def test_gets_metadata_from_schema(self) -> None:
        schema = {
            "$id": "https://example.com/schema.json",
            "title": "Example Schema",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"},
            },
            "required": ["name", "age"],
        }

        s = JsonSchema(schema)
        self.assertEqual(s.schema_id, "https://example.com/schema.json")
        self.assertEqual(s.schema_title, "Example Schema")
