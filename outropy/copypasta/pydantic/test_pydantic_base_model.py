import unittest
from typing import Optional

from pydantic import Field

from outropy.copypasta.pydantic.pydantic_base_model import PydanticBaseModel
from outropy.urn.urn import Urn


class TestModel(PydanticBaseModel):
    urn: Urn = Field(description="some urn")
    maybe_urn: Optional[Urn] = Field(description="maybe some urn")


class TestPydanticBaseModel(unittest.TestCase):
    def test_serializes_urn_to_str(self) -> None:
        urn = Urn.from_raw_identifier("a", "b", "c")
        t = TestModel(urn=urn, maybe_urn=None)

        t_as_json = t.model_dump_json()
        urn_str = str(urn)
        self.assertEqual(f'{{"urn":"{urn_str}","maybe_urn":null}}', t_as_json)
