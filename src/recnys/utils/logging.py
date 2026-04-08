import logging
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from logging import _SysExcInfoType
    from pathlib import Path

__all__ = ["setup_logging"]


class _NoTrackBackFormatter(logging.Formatter):
    @override
    def formatException(self, ei: _SysExcInfoType) -> str:
        notes = getattr(ei[1], "__notes__", [])
        if notes:
            return "\n".join(notes)
        return ""


def _get_console_handler() -> logging.StreamHandler:
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = _NoTrackBackFormatter(fmt="%(message)s")
    handler.setFormatter(formatter)

    return handler


def _get_file_handler(log_file: Path) -> logging.FileHandler:
    handler = logging.FileHandler(filename=log_file, mode="w", encoding="utf-8")
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    return handler


def setup_logging(log_file: Path, *, silent: bool, debug: bool) -> None:
    """Configure the top-level logger for recnys.

    Logging level:

    - If debug is True, set to DEBUG (overrides silent)
    - If silent is True, set to WARNING
    - Otherwise, set to INFO
    """
    logger = logging.getLogger("recnys")

    console_handler = _get_console_handler()
    logger.addHandler(console_handler)

    file_handler = _get_file_handler(log_file)
    logger.addHandler(file_handler)

    if silent:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.INFO)

    if debug:
        logger.setLevel(logging.DEBUG)
