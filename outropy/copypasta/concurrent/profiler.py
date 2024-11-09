import asyncio
import contextvars
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Coroutine, Dict, Generator, List, TypeVar

from outropy.copypasta.observability import logging

__all__ = ["with_task_group", "perf_counter", "install_profiler"]

profiler_logger = logging.get_logger_str(__name__)
tgname: contextvars.ContextVar[List[str]] = contextvars.ContextVar("tgname")
perf_counters: contextvars.ContextVar[Dict[str, float]] = contextvars.ContextVar(
    "perf-counters"
)
task_count = 0


T = TypeVar("T")


def task_factory_with_ctx_name(
    loop: asyncio.AbstractEventLoop,
    coro: Coroutine[Any, Any, T] | Generator[Any, None, T],
) -> asyncio.Future[T]:
    global task_count
    task = asyncio.tasks.Task(coro, loop=loop)
    task_c = task_count
    task_count += 1
    task_type = f"Task-{'-'.join(tgname.get([]))}-{task_c}"
    task.set_name(task_type)

    return task


# TODO track time + counts
def _merge_pc(target: Dict[str, float], src: Dict[str, float]) -> None:
    for k, v in src.items():
        target[k] = target.setdefault(k, 0.0) + v


@asynccontextmanager
async def with_task_group(name: str) -> AsyncGenerator[None, None]:
    old_name = tgname.get(None)
    old_pc = perf_counters.get(None)
    new_name = old_name + [name] if old_name else [name]
    loop = asyncio.get_event_loop()
    start = loop.time()
    token = tgname.set(new_name)
    perf_token = perf_counters.set({})
    try:
        yield None
    finally:
        tgname.reset(token)
        perf_c = perf_counters.get()
        perf_counters.reset(perf_token)
        if old_pc is not None:
            _merge_pc(old_pc, perf_c)
        duration = loop.time() - start
        profiler_logger.debug(f"{new_name} took {duration} sec perf-counters: {perf_c}")


@asynccontextmanager
async def perf_counter(name: str) -> AsyncGenerator[None, None]:
    loop = asyncio.get_event_loop()
    start = loop.time()
    perf_c = perf_counters.get(None)
    try:
        yield None
    finally:
        duration = loop.time() - start
        if perf_c is not None:
            perf_c[name] = perf_c.setdefault(name, 0.0) + duration


def install_profiler() -> None:
    asyncio.get_event_loop().set_task_factory(task_factory_with_ctx_name)
