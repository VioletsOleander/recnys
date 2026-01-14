import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

__all__ = ["get_file_hash", "prompt_for_confirmation"]


def get_file_hash(file_path: Path) -> str:
    with file_path.open("rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def prompt_for_confirmation(message: str, confirm_signals: Sequence[str]) -> bool:
    response = input(message).strip().lower()
    return response in confirm_signals
