import asyncio
from typing import AsyncIterator, List, TypeVar

T = TypeVar("T")


async def list_to_async_iterator(data: List[T]) -> AsyncIterator[T]:
    for item in data:
        yield item
        await asyncio.sleep(0)  # Yield control to the event loop
