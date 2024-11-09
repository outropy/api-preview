import unittest
from typing import Any, List, Sequence, Tuple

from outropy.copypasta.optional import flatten, only_one_not_none


class TestOptionalFlatten(unittest.TestCase):
    def test_flatten(self) -> None:
        expectations: List[Tuple[Sequence[Any], List[Any]]] = [
            (["a", "b", None, "c", "d", "e"], ["a", "b", "c", "d", "e"]),
            (["a", "b", None, "c", "d", "e"], ["a", "b", "c", "d", "e"]),
            (["a", "b", None, "c", "d", "e", "f"], ["a", "b", "c", "d", "e", "f"]),
            ([None, None, None], []),
            (["a", "b", "c"], ["a", "b", "c"]),
            ([], []),
            ([None, None, None, None], []),
            ([None, None, None, "a"], ["a"]),
            (["a", None, None, None], ["a"]),
            (["a", None, "b", None], ["a", "b"]),
            (["a", "b", None, "c", None], ["a", "b", "c"]),
            ([], []),
        ]

        for actual_input, expected in expectations:
            actual_result = flatten(actual_input)  # type: ignore
            self.assertEqual(
                sorted(actual_result),
                sorted(expected),
                f"Expected {expected}, got {actual_result} for input {actual_input}",
            )


class TestOnlyOneNotNone(unittest.TestCase):
    def test_it(self) -> None:
        expectations: List[Tuple[Sequence[Any], bool]] = [
            ([None, None, None, "a"], True),
            (["a", None, None, None], True),
            (["a", "b", None, "c", "d", "e"], False),
            (["a", "b", None, "c", "d", "e"], False),
            (["a", "b", None, "c", "d", "e", "f"], False),
            ([None, None, None], False),
            (["a", "b", "c"], False),
            ([], False),
            ([None, None, None, None], False),
            (["a", None, "b", None], False),
            (["a", "b", None, "c", None], False),
            ([], False),
        ]

        for actual_input, expected in expectations:
            result = only_one_not_none(*actual_input)
            self.assertEqual(result, expected, f"{actual_input} should be {expected}")
