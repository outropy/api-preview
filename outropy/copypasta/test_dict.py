import unittest
from typing import Any

from outropy.copypasta.dict import From
from outropy.copypasta.exceptions import KeyNotFoundError


class FromTest(unittest.TestCase):
    def test_bad_summary(self) -> None:
        f = From[str, str]({})
        self.assertEqual("", f.ensure_str("summary", ""))

    def test_ensure_path(self) -> None:
        f = From[str, Any]({"a": {"b": {"c": "d"}}})
        self.assertEqual({"b": {"c": "d"}}, f.ensure_path(["a"]))
        self.assertEqual({"c": "d"}, f.ensure_path(["a", "b"]))
        self.assertEqual("d", f.ensure_path(["a", "b", "c"]))

        with self.assertRaises(KeyNotFoundError):
            f.ensure_path(["a", "b", "c", "d"])
            f.ensure_path(["a", "b", "d"])

        self.assertEqual("x", f.ensure_path(["a", "b", "kc"], "x"))
        self.assertEqual("x", f.ensure_path(["a", "b", "c", "d"], "x"))
