from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

locks: Dict[str, bool] = {}


@asynccontextmanager
async def resource_try_lock(name: str) -> AsyncGenerator[bool, None]:
    if name in locks:
        yield False
        return

    try:
        locks[name] = True
        yield True
    finally:
        del locks[name]
