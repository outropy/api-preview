from typing import List, Optional, Protocol, Type, TypeVar

from outropy.copypasta.exceptions import IllegalArgumentError
from outropy.urn.urn import Urn, append_segment_to_urn


class HasUrn(Protocol):
    @property
    def urn(self) -> Urn:
        # fmt: off
        ...
        # fmt: on


class SupportsUrn(Protocol):
    urn_collection: str
    urn_namespace: str

    @property
    def urn(self) -> Urn:
        # fmt: off
        ...
        # fmt: on


T = TypeVar("T", bound=HasUrn)


def find_by_urn(desired: Urn, objects_with_urn: List[T]) -> Optional[T]:
    return next((u for u in objects_with_urn if u.urn == desired), None)


def is_a(urn: Urn, supported: SupportsUrn) -> bool:
    return (
        urn.namespace == supported.urn.namespace
        and urn.collection == supported.urn.collection
    )


def ensured_urn_is_for_type(urn: Urn, supported: Type[SupportsUrn]) -> Urn:
    if not urn.partial_urn == append_segment_to_urn(
        supported.urn_namespace, supported.urn_collection
    ):
        raise IllegalArgumentError(
            f"Expected URN to be of type [{append_segment_to_urn(supported.urn_namespace, supported.urn_collection)}], but got {urn}"
        )

    return urn
