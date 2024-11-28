import logging
import os
from typing import Any, Callable, Dict, Optional

from outropy.copypasta.json import json
from outropy.copypasta.optional import ensure


class ConfigException(Exception):
    pass


def env_config() -> Callable[[str, Optional[str]], Optional[str]]:
    def _get(key: str, default: Optional[str] = None) -> Optional[str]:
        return os.environ.get(key, default)

    return _get


def json_config() -> Callable[[str, Optional[str]], Optional[str]]:
    json_env = os.getenv("CONFIG_JSON")
    if json_env is None:
        raise ConfigException("CONFIG_JSON not set")
    env: Dict[str, Any] = json.loads(json_env)
    logging.warning(f"Config: {env}")

    def _get(key: str, default: Optional[str] = None) -> Optional[str]:
        return env[key] if key in env else default

    return _get


# Config is an object that reads the environment variables
class Config:
    def __init__(self) -> None:
        method = os.getenv("CONFIG_METHOD", "env")

        if method == "json":
            logging.warning("Using JSON config")
            self._get = json_config()
        else:
            logging.warning("Using ENV config")
            self._get = env_config()

    def __call__(self, key: str, default: Optional[str] = None) -> Optional[str]:
        return self._get(key, default)

    def ensured(self, key: str, default: Optional[str] = None) -> str:
        return ensure(
            self(key, default), f"Required config key {key} not found in {self}"
        )

    def get_required(self, key: str) -> Any:
        res = self(key)
        if res is None:
            raise ConfigException(f"Required config key {key} not found in {self}")
        return res

    def valid_config(self) -> bool:
        svc = self("SVC_NAME")
        return svc is not None and svc != ""

    def app_base_url(self) -> str:
        return self("APP_BASE_URL") or "http://localhost:8080"

    def _redacted(self, maybe_value: Optional[str]) -> Optional[str]:
        return f"REDACTED ({len(maybe_value)} chars)" if maybe_value else None

    def get_bool(self, key: str, default: Optional[bool] = None) -> Optional[bool]:
        res = self.ensured(key, "false").lower()
        return res in {"1", "on", "true", "yes"}

    def __str__(self) -> str:
        return self.__repr__()

    def __repr__(self) -> str:
        sorted_kv: str = ""
        safe_to_print = self._safe_to_print()
        sorted_keys = sorted(safe_to_print.keys())
        for key in sorted_keys:
            sorted_kv += f"{key}={safe_to_print[key]},"
        return f"Config({sorted_kv})"

    def _safe_to_print(self) -> Dict[str, Optional[str]]:
        return {k: self._redacted(v) for k, v in os.environ.items()}


class InMemoryConfig(Config):
    def __init__(self, cfg: Dict[str, str]) -> None:
        self.cfg = cfg
        super().__init__()

    def __call__(self, key: str, default: Any = None) -> Any:
        return self.cfg.get(key, default)

    def valid_config(self) -> bool:
        svc = self("SVC_NAME")
        return svc is not None and svc != ""


class FileConfig(Config):
    def __init__(self, file_name: str) -> None:
        super().__init__()
        self.cfg: Dict[str, str] = {}

        def trim_quotes(string_to_trim: str) -> str:
            if string_to_trim[0] == '"' or string_to_trim[0] == "'":
                string_to_trim = string_to_trim[1:]
            if string_to_trim[-1] == '"' or string_to_trim[-1] == "'":
                string_to_trim = string_to_trim[0:-1]
            return string_to_trim

        for line in open(file_name, "r").readlines():
            line = line.strip()
            if len(line) == 0 or line[0] == "#":
                # We support a special marker to when the export section ends and the scripting starts
                # This is mostly so those scripts can be used to modify your PS1
                if line == "#end export":
                    break
                continue
            if not line.startswith("export "):
                logging.warning(
                    f"Invalid config line (doesn't start with export): {line}"
                )
                continue
            line = line[len("export ") :]  # noqa: E203
            try:
                idx = line.index("=")
            except BaseException as e:
                logging.warning(f"Invalid config line (no = sign on it): {line}: {e}")
                continue
            key = line[0:idx].strip()
            value = trim_quotes(line[idx + 1 :].strip())  # noqa: E203
            self.cfg[key] = value

    def __call__(self, key: str, default: Any = None) -> Any:
        return self.cfg.get(key, default)

    def valid_config(self) -> Any:
        svc = self("SVC_NAME")
        return svc is not None and svc != ""
