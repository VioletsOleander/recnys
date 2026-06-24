import logging
from pathlib import Path
from typing import TYPE_CHECKING, override

if TYPE_CHECKING:
    from logging import _SysExcInfoType

__all__ = ["setup_logger"]


def setup_logger(*, silent: bool, debug: bool) -> None:
    """Configure the handlers and logging level for the top-level logger.

    The logger by default only has a console handler, and has INFO logging level.

    Args:
        silent (bool): If True, the logging level is set to WARNING.
        debug (bool): If True, the logging level is set to DEBUG (overrides `silent`).
            An additional file handler will also be added.
    """
    logger = logging.getLogger("recnys")
    logger.handlers.clear()

    console_handler = _get_console_handler()
    logger.addHandler(console_handler)

    if not silent and not debug:
        logger.setLevel(logging.INFO)
    elif silent and not debug:
        logger.setLevel(logging.WARNING)
    else:
        logger.setLevel(logging.DEBUG)
        file_handler = _get_file_handler(Path.cwd() / "recnys.log")
        logger.addHandler(file_handler)


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
