# TODO: standardize suffix as Exception?
from typing import Any, Optional


class IllegalStateError(Exception):
    """Exception raised when an object is in an illegal state."""

    pass


class ExpectedButNorFoundError(Exception):
    pass


class IllegalArgumentError(Exception):
    """Exception raised when an argument is illegal."""

    pass


class IllegalOperation(Exception):
    """Exception raised when an operation is illegal."""

    pass


class NotFoundError(Exception):
    """Exception raised when something is not found."""

    pass


class ObjectNotFoundError(NotFoundError):
    def __init__(self, urn: "Urn") -> None:  # type: ignore
        super().__init__(f"Object not found for URN: [{urn}]")


class KeyNotFoundError(NotFoundError):
    """Exception raised when a key is not found in some sort of dictionary."""

    pass


# Then in your code:


class MaxRetriesExceededException(Exception):
    """Exception raised when an operation is illegal."""

    pass


class NotImplemetedYetError(Exception):
    def __init__(self, instance: Any, function: Optional[str] = None):
        if function:
            super().__init__(
                f"[{instance.__class__.__name__}.{function}] not implemented yet"
            )
        else:
            super().__init__(
                f"Function not implemented in [{instance.__class__.__name__}] yes"
            )
