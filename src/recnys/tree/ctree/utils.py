import functools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["handle_fnf"]


def handle_fnf[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Decorator to handle FileNotFoundError exceptions raised from the decorated function."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as e:
            e.add_note("Hint: Please check recnys.yaml to ensure the specified path exists.")
            raise

    return wrapper
