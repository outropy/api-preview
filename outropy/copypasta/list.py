import math
from collections import deque
from typing import Callable, List, Optional, TypeVar

from outropy.copypasta.exceptions import IllegalArgumentError

T = TypeVar("T")
U = TypeVar("U")


def dedupe(lst: List[T]) -> List[T]:
    return list(set(lst))


def convert_list(input_list: List[T]) -> List[U]:
    # TODO: this is super unsafe, but I'm in a hurry
    new: List[U] = [item for item in input_list]  # type: ignore
    return new


def ensure_list(input_list: T | List[T] | Optional[T]) -> List[T]:
    if input_list is None:
        return []
    if isinstance(input_list, list):
        return input_list
    return [input_list]


def partition_list(lst: List[T], batch_size: int) -> List[List[T]]:
    if batch_size <= 0:
        raise IllegalArgumentError("Batch size must be greater than 0")
    return [lst[i : i + batch_size] for i in range(0, len(lst), batch_size)]


def list_of_str(input_list: List[T]) -> List[str]:
    return [str(item) for item in input_list]


def bucketize_list(arr: List[T], fun: Callable[[T, int], bool]) -> List[List[T]]:
    copy = deque(arr)
    res: List[List[T]] = []
    wip: List[T] = []
    while len(copy) > 0:
        x = copy.popleft()
        if fun(x, len(wip)):
            wip.append(x)
        else:
            if len(wip) > 0:
                res.append(wip)
            wip = [x]
    if len(wip) > 0:
        res.append(wip)
    return res


def bucketize_by_key(arr: List[T], fun: Callable[[T], U]) -> List[List[T]]:
    res: List[List[T]] = []
    wip: List[T] = []
    if len(arr) == 0:
        return []
    current_key: U = fun(arr[0])
    for val in arr:
        key = fun(val)
        if key == current_key:
            wip.append(val)
        else:
            if len(wip) > 0:
                res.append(wip)
            wip = [val]
            current_key = key
    if len(wip) > 0:
        res.append(wip)
    return res


def split_into_buckets(lst: List[T], num_buckets: int) -> List[List[T]]:
    # split into num_buckets buckets
    return partition_list(lst, int(math.ceil(len(lst) / num_buckets)))
