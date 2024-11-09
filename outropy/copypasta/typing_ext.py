from typing import Any, Protocol, Sequence, Set, Type, TypeVar, Union

T = TypeVar("T")

# I don't understand why, but we can't use Container[T]
HAS_CONTAINS = Union[Sequence[T], Set[T]]


def obj_in(obj: T, container: HAS_CONTAINS[T]) -> bool:
    return obj in container


class SupportsStr(Protocol):
    def __str__(self) -> str:
        # fmt: off
        ...
        # fmt: on


class TypeCheckError(Exception):
    def __init__(self, obj: Any, expected_type: Type[Any]) -> None:
        self.obj = obj
        self.expected_type = expected_type

    def __str__(self) -> str:
        return f"Expected type [{self.expected_type}], but got [{type(self.obj)}] for [{self.obj}]"


ExpectedType = TypeVar("ExpectedType")


def ensured_is_a(obj: Any, expected_type: Type[ExpectedType]) -> ExpectedType:
    if not isinstance(obj, expected_type):
        raise TypeCheckError(obj, expected_type)
    return obj
