from typing import List
from unittest import TestCase

from outropy.copypasta.exceptions import IllegalArgumentError
from outropy.copypasta.list import bucketize_list, partition_list


class TestListPartition(TestCase):
    def test_partition_normal_and_edge_cases(self) -> None:
        urns: List[str] = [f"urn{i}" for i in range(12)]

        # Normal case: batch size 4, evenly divided
        result = partition_list(urns, 4)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 4)
        self.assertEqual(len(result[1]), 4)
        self.assertEqual(len(result[2]), 4)

        # Edge case: batch size larger than list
        result = partition_list(urns, 20)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), len(urns))

        # Edge case: batch size equal to list length
        result = partition_list(urns, 12)
        self.assertEqual(len(result), 1)
        self.assertEqual(len(result[0]), 12)

        # Edge case: batch size smaller than list length
        result = partition_list(urns, 3)
        self.assertEqual(len(result), 4)
        self.assertEqual(len(result[0]), 3)
        self.assertEqual(len(result[-1]), 3)

    def test_partition_invalid_cases(self) -> None:
        urns: List[str] = [f"urn{i}" for i in range(12)]

        # Edge case: empty list
        empty_list: List[int] = []
        result: List[List[int]] = partition_list(empty_list, 4)
        self.assertEqual(result, empty_list)

        # Invalid case: batch size zero
        with self.assertRaises(IllegalArgumentError):
            partition_list(urns, 0)

        # Invalid case: batch size negative
        with self.assertRaises(IllegalArgumentError):
            partition_list(urns, -1)

    def test_bucktizer_happy_path(self) -> None:
        result = bucketize_list([1, 2, 3, 4, 5, 6, 7], lambda _, size: size < 3)
        expected = [[1, 2, 3], [4, 5, 6], [7]]

        self.assertEqual(result, expected)

    def test_bucketizer_split_at_odds(self) -> None:
        result = bucketize_list(
            [1, 2, 3, 4, 5, 6, 7, 8, 8], lambda item, _: (item % 2) == 0
        )
        expected = [[1, 2], [3, 4], [5, 6], [7, 8, 8]]

        self.assertEqual(result, expected)
