# ruff: noqa: TRY401

import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from .platform import UnsupportedPlatformError

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

__all__ = ["handle_exceptions"]

logger = logging.getLogger(__name__)


def handle_exceptions(func: Callable[[], int]) -> Callable[[], int]:
    """Decorator to handle exceptions raised from the decorated function.

    Primarily used for decorating the main function.
    """

    def wrapper() -> int:
        try:
            return func()
        except FileNotFoundError as e:
            logger.exception("Error: File not found: %s", e.filename)
            return 1
        except ValidationError as e:

            def messages(e: ValidationError) -> Generator[str]:
                for err in e.errors():
                    field = f"'{' -> '.join(map(str, err['loc']))}'"
                    yield f"  {field}: {err['msg']}."

            logger.exception(
                "Error: Data validation failed.\nDetails:\n%s",
                "\n".join(messages(e)),
            )

            return 1
        except UnsupportedPlatformError as e:
            logger.exception("Error: %s", e)
            return 1
        except KeyboardInterrupt:
            logger.exception("Execution interrupted by user, program exited.")
            return 1
        except Exception as e:
            logger.exception("Unexpected error: %s", e)
            logger.info(
                "Check the log file '.recnys/recnys.log' for more details if debug mode is enabled."
            )
            return 1

    return wrapper
