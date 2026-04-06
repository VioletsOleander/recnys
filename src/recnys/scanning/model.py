"""Provide data models for scanned configuration and variables."""

from enum import StrEnum

from pydantic import BaseModel, RootModel

__all__ = ["Dest", "EntryValue", "Policy", "ScannedConfig", "ScannedVariables"]


class Policy(StrEnum):
    """The file synchronization policy.

    Attributes:
        COPY: The source file will be copied to the destination path.
        SYMLINK: A symbolic link will be created at the destination path pointing to the source file.
    """

    COPY = "copy"
    SYMLINK = "symlink"


class Dest(BaseModel):
    """Destination paths for different platforms.

    Attributes:
        Linux (str | None): The destination path for Linux, or None if not specified.
        Windows (str | None): The destination path for Windows, or None if not specified.
    """

    Linux: str | None = None
    Windows: str | None = None


class EntryValue(BaseModel):
    """Scanned entry value.

    Attributes:
        dest (Dest | None): The destination paths for different platforms, or None if not specified.
        policy (Policy | None): The synchronization policy, or None if not specified.
    """

    dest: Dest | None = None
    policy: Policy | None = None


class ScannedConfig(RootModel):
    """Key-value pairs scanned from the YAML configuration data.

    Key (str): The source path.
    Value (EntryValue | None): The destination and policy, or None if not specified.
    """

    root: dict[str, EntryValue | None]

    def __getitem__(self, key: str) -> EntryValue | None:
        return self.root[key]


class ScannedVariables(RootModel):
    """Key-value pairs scanned from the YAML variables data.

    Key (str): The name of the variable.
    Value (str): The value of the variable.
    """

    root: dict[str, str]

    def __getitem__(self, key: str) -> str:
        return self.root[key]
