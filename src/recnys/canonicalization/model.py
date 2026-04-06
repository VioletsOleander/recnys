"""Provide `CanonicalConfig` and related data structures."""

from typing import TYPE_CHECKING

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.parsing.model import Policy

__all__ = ["CanonicalizedConfig", "EntryKey", "EntryValue"]


class EntryKey(BaseModel):
    """Canonicalized entry key.

    Attributes:
        src (str): The absolute source path.
        static (bool): True for static, False for dynamic. Refers to features/README:pattern-definition
            for the meaning of "static", "dynamic".
    """

    src: Path
    static: bool


class EntryValue(BaseModel):
    """Canonicalized entry value.

    Attributes:
        dest (Path): The absolute destination path.
        policy (Policy): The synchronization policy.
    """

    dest: Path
    policy: Policy


class CanonicalizedConfig(RootModel):
    """Key-value pairs representing the canonicalized configuration."""

    root: dict[EntryKey, EntryValue]
