import inspect
import sys
from typing import Any, List, Optional, Protocol, Sequence, Set, Type, TypeVar, Union

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


def find_subclass_by_name(class_name: str, base_class: Type[T]) -> Optional[Type[T]]:
    modules: List[Any] = list(sys.modules.values())

    for module in modules:
        if module is None:
            continue
        try:
            for _, cls in inspect.getmembers(module):
                if (
                    inspect.isclass(cls)
                    and issubclass(cls, base_class)
                    and cls.__name__ == class_name
                    and cls != base_class
                ):
                    return cls
        except ImportError:
            # Skip modules that can't be inspected
            continue

    return None
