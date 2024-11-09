from test.async_test_case import AsyncTestCase
from typing import AsyncIterator

from openai import BaseModel
from pydantic import Field

from outropy.copypasta.async_iterator import list_to_async_iterator


class SomeObj(BaseModel):
    payload: str = Field(description="The chunk of plaintext")


class TestAsyncIterator(AsyncTestCase):
    async def test_returns_each_element(self) -> None:
        lists = [
            [],
            ["a", "b", "c"],
            [903241, 123, 123],
            [1, "a", 1.0],
            [SomeObj(payload="hello"), SomeObj(payload="world")],
        ]

        for lst in lists:
            async_iter: AsyncIterator = list_to_async_iterator(lst)  # type: ignore
            materialized = []
            async for item in async_iter:
                materialized.append(item)

            self.assertEqual(lst, materialized)
