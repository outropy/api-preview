from typing import Any, Dict, Generic, Optional, Sequence, TypeVar

from outropy.copypasta.exceptions import KeyNotFoundError

TK = TypeVar("TK")
TV = TypeVar("TV")


class From(Generic[TK, TV]):
    def __init__(self, d: Dict[TK, TV]) -> None:
        self.d = d

    def get(self, key: TK, default_value: Optional[TV] = None) -> Optional[TV]:
        return self.d.get(key, default_value)

    def get_str(self, key: TK, default_value: Optional[str] = None) -> Optional[str]:
        maybe_str = self.d.get(key, default_value)
        return str(maybe_str) if maybe_str is not None else None

    def ensure_str(self, key: TK, default_value: Optional[str] = None) -> str:
        val = self.get_str(key, default_value)
        if val is None or not isinstance(val, str):
            raise KeyNotFoundError(f"Key:{key} not found")
        return val

    def ensure_any(self, key: TK, default_value: Optional[Any] = None) -> Any:
        val = self.get(key, default_value)
        if val is None:
            raise KeyNotFoundError(f"Key:{key} not found")
        return val

    def ensure_bool(self, key: TK, default_value: Optional[bool] = None) -> bool:
        val: Any = self.d.get(key, None)
        if val is None:
            val = default_value
        if val is None or not isinstance(val, bool):
            raise KeyNotFoundError(f"Key:{key} not found")
        return val is True

    def ensure_path(
        self, path: Sequence[TK], default_value: Optional[Any] = None
    ) -> Any:
        obj: Dict[TK, Any] = self.d
        val: Any = None
        for key in path:
            if not isinstance(obj, dict):
                if default_value is not None:  # type: ignore[unreachable]
                    return default_value
                else:
                    raise KeyNotFoundError(f"Path:{path} not found")
            else:
                val = obj.get(key)
                if val is None:
                    if default_value is not None:
                        return default_value
                    raise KeyNotFoundError(f"Path:{path} not found")
                obj = val
        if val is None:
            if default_value is not None:
                return default_value
            raise KeyNotFoundError(f"Path:{path} not found")
        return val
