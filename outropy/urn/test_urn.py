import json
import unittest
from typing import Dict
from uuid import UUID

from pydantic import BaseModel

from outropy.copypasta.exceptions import IllegalArgumentError
from outropy.urn.urn import Urn


class SomeUrnSupported:
    urn_namespace = "unittest"
    urn_collection = "some-urn-supported"

    @property
    def urn(self) -> Urn:
        return Urn.from_raw_identifier(self.urn_namespace, self.urn_collection, "1")


class SimpleModel(BaseModel):
    name: str
    urn: Urn


class TestUrn(unittest.TestCase):
    def test_checks_if_is_a(self) -> None:
        u = Urn.from_raw_identifier("unittest", "some-urn-supported", "1")
        self.assertTrue(u.is_a(SomeUrnSupported))

    def test_renders_as_string(self) -> None:
        expectations: Dict[Urn, str] = {
            Urn.from_raw_identifier(
                "unittest", "some-urn-supported", "1"
            ): f"unittest:some-urn-supported:{Urn.encode_id_for_latest('unittest', 'some-urn-supported', '1')}",
            Urn.from_raw_identifier(
                "unittest", "some-urn-supported", "2"
            ): f"unittest:some-urn-supported:{Urn.encode_id_for_latest('unittest', 'some-urn-supported', '2')}",
        }
        for urn, expected in expectations.items():
            self.assertEqual(str(urn), expected)

    def test_equals(self) -> None:
        u1 = Urn.from_raw_identifier("unittest", "some-urn-supported", "1")
        u2 = Urn.from_raw_identifier("unittest", "some-urn-supported", "1")
        u3 = Urn.parse(
            f"unittest:some-urn-supported:{Urn.encode_id_for_latest('unittest', 'some-urn-supported', '1')}"
        )
        u4 = Urn.from_raw_identifier("unittest", "some-urn-supported", "2")
        self.assertEqual(u1, u2)
        self.assertEqual(u1, u3)
        self.assertNotEqual(u1, u4)

    def test_rejects_invalid_segments(self) -> None:
        invalid_segments = [
            # TODO: "None", this will require changing a lot of inrelated tests
            "",
            " ",
            " a",
            "a ",
            "a b",
            "a:b",
            "a::b",
            "a:b:",
            ":a:b",
            "a:b:c",
            "a|b" "a_b",
        ]

        for segment in invalid_segments:
            with self.assertRaises(IllegalArgumentError, msg=f"segment: {segment}"):
                Urn.from_raw_identifier("something", segment, "else")

    def test_rejects_invalid_identifier(self) -> None:
        invalid_identifiers = [
            "",
            " ",
            "something:here",
        ]

        valid_identifiers = [
            "something",
            "something_here",
            "something-here",
            "Something-Here",
            "something_here_",
            "_something_here",
            "something_here_",
            "something_here_",
            "c_1882hqfdsjasrp8igblmmqip430s7cge@resource.calendar.google.com",
            "3242",
            "-23",
        ]

        for identifier in invalid_identifiers:
            with self.assertRaises(IllegalArgumentError):
                Urn.from_raw_identifier("ns", "cl", identifier)

        for identifier in valid_identifiers:
            urn = Urn.from_raw_identifier("ns", "cl", identifier)
            self.assertEqual(identifier, urn.identifier)
            self.assertEqual(identifier, Urn.parse_encoded_urn(str(urn)).identifier)

    def test_raw_to_versioned_and_back(self) -> None:
        urn = Urn.from_raw_identifier("a", "b", "c")
        urn2 = Urn.from_encoded_identifier("a", "b", urn.encoded_identifier)
        self.assertEqual(urn, urn2)

    def test_encoding(self) -> None:
        enc = Urn.encode_id_for_latest("ns", "col", "foo")
        dec = Urn.decode_identifier("ns", "col", enc)
        self.assertEqual("foo", dec)

    def test_uuid_urn(self) -> None:
        urn0 = Urn.from_uuid("ns", "col", UUID("123e4567-e89b-12d3-a456-426614174000"))
        self.assertTrue(urn0.has_uuid)
        self.assertEqual(
            UUID("123e4567-e89b-12d3-a456-426614174000"), urn0.uuid_identifier
        )

        urn1 = Urn.from_raw_identifier("url", "col", "99")
        self.assertFalse(urn1.has_uuid)
        with self.assertRaises(IllegalArgumentError):
            urn1.uuid_identifier

    def test_json_serialization_roundtrip(self) -> None:
        m = SimpleModel(name="foo", urn=Urn.from_raw_identifier("ns", "col", "foo"))
        enc = m.model_dump_json()
        dec = SimpleModel.model_validate_json(enc)
        self.assertEqual(dec.urn, m.urn)

        m = SimpleModel(
            name="foo",
            urn=Urn.from_uuid(
                "ns", "col", UUID("123e4567-e89b-12d3-a456-426614174000")
            ),
        )
        enc = m.model_dump_json()
        dec = SimpleModel.model_validate_json(enc)
        self.assertEqual(dec.urn, m.urn)

        dec = SimpleModel.model_validate(json.loads(enc))
        self.assertEqual(dec.urn, m.urn)
