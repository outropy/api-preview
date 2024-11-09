from typing import Dict, List, Set, Tuple
from unittest import TestCase

from outropy.copypasta.typing_ext import TypeCheckError, ensured_is_a


class TestEnsuredIsA(TestCase):
    def test_ensured_is_a(self) -> None:
        expected_true = {
            str: "string here",
            int: 123,
            float: 123.456,
            bool: True,
            List: [1, 2, 3],
            Tuple: (1, 2, 3),
            Set: {1, 2, 3},
            Dict: {1: 2, 3: 4},
            TestCase: self,
        }
        for expected_type, obj in expected_true.items():
            self.assertEqual(obj, ensured_is_a(obj, expected_type))  # type: ignore

        expected_false = {
            int: "string here",
            str: 123,
            bool: 123.456,
            TestCase: True,
            List: (1, 2, 3),
            Tuple: [1, 2, 3],
        }
        for expected_type, obj in expected_false.items():
            with self.assertRaises(TypeCheckError):
                ensured_is_a(obj, expected_type)  # type: ignore
