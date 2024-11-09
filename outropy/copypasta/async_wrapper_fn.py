import inspect
from typing import Any, Callable, Coroutine


def async_wrapper_fn(
    func: Callable[..., Any]
) -> Callable[..., Coroutine[Any, Any, Any]]:
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        # Get the signature of the function
        sig = inspect.signature(func)

        # Bind the provided arguments to the signature
        bound_args = sig.bind_partial(*args, **kwargs)

        # Call the function with the bound arguments
        return func(*bound_args.args, **bound_args.kwargs)

    return async_wrapper
