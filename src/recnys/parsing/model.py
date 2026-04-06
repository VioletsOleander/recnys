"""Provide `ParsedConfig` and related data structures."""

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from recnys.scanning.model import Policy

__all__ = ["EntryKey", "EntryValue", "KeyAttribute", "KeyCategory", "ParsedConfig"]


class KeyAttribute(NamedTuple):
    """The attribute of an entry key.

    Refers to features/README:pattern-definition for the meaning of
    "static", "dynamic", "root" and "leaf".

    Note that the concept of "static/dynamic", "root/leaf" currently only
    affect the handling for file entries.

    Attributes:
        static (bool): True for static, False for dynamic.
        root (bool): True for root, False for leaf.
    """

    static: bool
    root: bool


class KeyCategory(Enum):
    """The category of an entry key.

    Attributes:
        FILE
        DIRECTORY
    """

    FILE = "File"
    DIRECTORY = "Directory"


class EntryKey(BaseModel):
    """Parsed entry key.

    Attributes:
        src (str): The source path, relative to the repository root directory.
        category (KeyCategory): The category of the entry key.
        attribute (KeyAttribute): The attribute of the entry key.
    """

    src: str
    category: KeyCategory
    attribute: KeyAttribute


class EntryValue(BaseModel):
    """Parsed entry value.

    Attributes:
        dest (str): The destination path, relative to the home directory.
        policy (Policy): The synchronization policy.
    """

    dest: str
    policy: Policy


class ParsedConfig(RootModel):
    """Key-value pairs representing the parsed configuration."""

    root: dict[EntryKey, EntryValue]
