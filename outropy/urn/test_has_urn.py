import unittest

from outropy.urn.has_urn import find_by_urn
from outropy.urn.urn import Urn


class StubHasUrn:
    def __init__(self, urn_identifier: str) -> None:
        self.urn = Urn.from_raw_identifier("test", "t", urn_identifier)


class TestHasUrn(unittest.TestCase):
    def test_find_by_urn(self) -> None:
        expected = StubHasUrn("foo")

        others = [StubHasUrn("bar"), StubHasUrn("baz")]

        self.assertIsNone(find_by_urn(expected.urn, others))
        self.assertEquals(expected, find_by_urn(expected.urn, [expected] + others))
