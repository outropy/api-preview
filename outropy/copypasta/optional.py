from typing import Coroutine, List, Optional, Sequence, TypeVar

T = TypeVar("T")


def ensure(value: Optional[T], error_msg: str = "Used ensure on None") -> T:
    assert value is not None, error_msg
    return value


async def aensure(
    future_value: Coroutine[None, None, Optional[T]],
    error_msg: str = "Used ensure on None",
) -> T:
    value = await future_value
    assert value is not None, error_msg
    return value


def remove_nones_from(lst: Sequence[Optional[T]]) -> List[T]:
    return [x for x in lst if x is not None]


# TODO "Use remove_nones instead"
def flatten(lst: Sequence[Optional[T]]) -> List[T]:
    return remove_nones_from(lst)


def first_if_any(lst: Sequence[T]) -> Optional[T]:
    return lst[0] if len(lst) > 0 else None


def equals_if_any(maybe_value: Optional[T], value: T) -> bool:
    if maybe_value is None:
        return False
    else:
        return maybe_value == value


def only_one_not_none(*args: Optional[T]) -> bool:
    return sum(1 for x in args if x is not None) == 1
