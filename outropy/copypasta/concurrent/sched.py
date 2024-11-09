import asyncio
from datetime import timedelta
from typing import Any, Awaitable, Callable, Coroutine, Optional

from outropy.copypasta.observability import logging


class Scheduler:
    def __init__(self) -> None:
        self.logger = logging.get_logger(self)

    def schedule(
        self,
        fun: Callable[..., Awaitable],  # type: ignore
        frequency: timedelta,
        delay_start: bool = False,
        name: Optional[str] = None,
        verbose: bool = False,
        run_once: bool = False,
        **exec_args: Any,
    ) -> asyncio.Task[None]:
        async def run_task() -> None:
            if delay_start:
                await asyncio.sleep(frequency.total_seconds())
            loop = asyncio.get_running_loop()
            while not loop.is_closed():
                await fun(**exec_args)
                await asyncio.sleep(frequency.total_seconds())

        return asyncio.create_task(run_task())

    def sync_submit(self, fun: Coroutine) -> None:  # type: ignore
        async def run_task() -> None:
            await fun

        asyncio.create_task(run_task())
