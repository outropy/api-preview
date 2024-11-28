import logging
from typing import Any, Iterable, Optional

import structlog
from structlog.typing import Processor

from outropy.copypasta.config.config import Config

log_in_json = False
log_level = "INFO"
global_logger = None


def setup_structlog(json_logs: bool, log_level: str) -> None:
    root = logging.getLogger()
    # Remove all existing handlers
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    """Set up structlog and logging."""
    # Initialize the Python logging module
    logging.basicConfig(level=log_level, handlers=[logging.StreamHandler()])
    processors: Iterable[Processor] = []
    # Set up processors: If json_logs is True, use JSON, otherwise use the console-friendly format
    if json_logs:
        processors = [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.add_log_level,
            structlog.processors.JSONRenderer(),
        ]
    else:
        processors = [
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.stdlib.add_log_level,
            structlog.dev.ConsoleRenderer(),
        ]

    # Bind structlog to logging
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


class Logging:
    def __init__(self, config: Config) -> None:
        cfg_log_in_json = config("LOG_JSON_FORMAT", "False") == "True"
        cfg_log_level = str(config("LOG_LEVEL", "INFO")).upper()

        setup_structlog(json_logs=cfg_log_in_json, log_level=cfg_log_level)
        # Not needed: global_logger = structlog.stdlib.get_logger(name)
        # Using the below line to ensure logs are produced upon initialization
        structlog.get_logger("Logging").info(
            "Logging initialized", level=cfg_log_level, json=cfg_log_in_json
        )


def get_logger(obj: Any, suffix: Optional[Any] = None) -> Any:
    # surely there's a less stupid way of doing this with structured logging?
    logger_name = type(obj).__name__
    if suffix:
        logger_name = f"{logger_name}[{suffix.__str__()}]"
    return get_logger_str(logger_name)


def get_logger_str(name: str) -> Any:
    return structlog.get_logger(name)


def extract_python_logger(structlog__logger: Any) -> logging.Logger:
    return structlog__logger._logger  # type: ignore
