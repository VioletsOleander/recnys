"""Provide `CanonicalConfig` and related data structures.

`CanonicalConfig` is the central data structure that modules in this project
communicate with.
"""

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, RootModel

__all__ = ["CanonicalConfig", "EntryKey", "EntryValue", "KeyCategory"]


class KeyCategory(StrEnum):
    """The category of an entry key specified in the configuration file.

    The category is determined by the suffix of the source path specified in the configuration file:

    Attributes:
        STATIC_FILE: The entry key is a static file if it does not end with "/" or ".template".
        DYNAMIC_FILE: The entry key is a dynamic file if it ends with ".template".
        DIRECTORY: The entry key is a directory if it ends with "/".
    """

    STATIC_FILE = "StaticFile"
    DYNAMIC_FILE = "DynamicFile"
    DIRECTORY = "Directory"


class EntryKey(BaseModel):
    """Source path and category of an entry key specified in the configuration file.

    Attributes:
        src (str): The source path specified in the configuration file.
        category (KeyCategory): The category of the entry key.
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
    children: list[EntryKey] = []


class EntryValue(BaseModel):
    """Destination path and synchronization policy for a source path specified in the configuration file.

    Attributes:
        dest (str): The destination path for the source path.
        policy (Literal["Copy", "Symlink"]): The file synchronization policy for the source path.
    """

    dest: str
    policy: Literal["Copy", "Symlink"]


class CanonicalConfig(RootModel):
    """Key-value pairs representing the canonicalized configuration.

    Key (EntryKey): The source path and category of the entry.
    Value (EntryValue): The destination path and synchronization policy for the entry.
    """

    root: dict[EntryKey, EntryValue]
