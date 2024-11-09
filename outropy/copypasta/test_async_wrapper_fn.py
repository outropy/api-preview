import datetime
import unittest

from outropy.copypasta.async_wrapper_fn import async_wrapper_fn
from outropy.copypasta.clock.clock import SystemClock


class TestAsyncWrapperFn(unittest.IsolatedAsyncioTestCase):
    async def test_async_wrapper_fn(self) -> None:
        f = lambda x: x + 1  # noqa: E731
        async_f = async_wrapper_fn(f)
        self.assertEqual(f(1), await async_f(1))  # type: ignore

        def f2(x: int, y: datetime.datetime) -> int:
            return x + y.year

        async_f2 = async_wrapper_fn(f2)
        d = SystemClock.at(2020, 1, 1)
        self.assertEqual(f2(1, d), await async_f2(1, d))
