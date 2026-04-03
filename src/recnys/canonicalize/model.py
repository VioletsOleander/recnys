"""Provide `CanonicalConfig` and related data structures.

`CanonicalConfig` is the central data structure that modules in this project
communicate with.
"""

from enum import Enum
from typing import TYPE_CHECKING, NamedTuple

from pydantic import BaseModel, RootModel

if TYPE_CHECKING:
    from recnys.config.model import Policy

__all__ = ["CanonicalConfig", "EntryKey", "EntryValue", "KeyAttribute", "KeyCategory"]


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
    """Source path and category of an entry key specified in the configuration file.

    Attributes:
        src (str): The source path specified in the configuration file, relative to current working directory.
        category (KeyCategory): The category of the entry key.
        attribute (KeyAttribute): The attribute of the entry key.
        children (list[EntryKey]):
            For file entry: empty list
            For directory entry that does not contain other entries: empty list
            For directory entry that contains other entries: list of EntryKey for the entries
                contained by the directory
            The meaning of "contain" here refers to the path relationship, i.e. directories and its
            containing files and subdirectories.
    """

    src: str
    category: KeyCategory
    attribute: KeyAttribute
    children: list[EntryKey] = []


class EntryValue(BaseModel):
    """Destination path and synchronization policy for a source path specified in the configuration file.

    Attributes:
        dest (str): The destination path for the source path, relative to the home directory.
        policy (Policy): The file synchronization policy for the source path.
    """

    dest: str
    policy: Policy


class CanonicalConfig(RootModel):
    """Key-value pairs representing the canonicalized configuration."""

    root: dict[EntryKey, EntryValue]
