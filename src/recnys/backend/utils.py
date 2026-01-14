import hashlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

__all__ = ["get_file_hash", "prompt_for_confirmation"]


def get_file_hash(file_path: Path) -> str:
    sha256 = hashlib.sha256()
    with file_path.open("rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def prompt_for_confirmation(message: str, confirm_signals: Sequence[str]) -> bool:
    response = input(message).strip().lower()
    return response in confirm_signals
