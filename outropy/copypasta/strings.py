from typing import Any, Optional

from outropy.copypasta.typing_ext import SupportsStr


def safe_trim(s: Any, max_len: int = 2000) -> Optional[str]:
    return str(s)[:max_len] if s is not None else None


def ellipsize(s: str, max_len: int = 2000) -> str:
    return s[:max_len].rstrip() + "..." if len(s) > max_len else s


def maybe_to_str(v: Optional[SupportsStr]) -> Optional[str]:
    return str(v) if v is not None else None
