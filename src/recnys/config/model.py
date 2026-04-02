"""Provide data models for loaded configuration and variables."""

from enum import StrEnum

from pydantic import BaseModel, RootModel

__all__ = ["Dest", "EntryValue", "LoadedConfig", "LoadedVariables", "Policy"]


class Policy(StrEnum):
    """The file synchronization policy specified in the configuration file.

    Attributes:
        COPY: The source file will be copied to the destination path.
        SYMLINK: A symbolic link will be created at the destination path pointing to the source file.
    """

    COPY = "copy"
    SYMLINK = "symlink"


class Dest(BaseModel):
    """Destination paths for different platforms specified in the configuration file.

    Attributes:
        Linux (str | None): The destination path for Linux, or None if not specified.
        Windows (str | None): The destination path for Windows, or None if not specified.
    """

    Linux: str | None = None
    Windows: str | None = None


class EntryValue(BaseModel):
    """Destination and policy for a source path specified in the configuration file.

    Attributes:
        dest (Dest | None): The destination paths for different platforms, or None if not specified
        policy (Policy | None): The file synchronization policy, or None if not specified.
    """

    dest: Dest | None = None
    policy: Policy | None = None


class LoadedConfig(RootModel):
    """Key-value pairs loaded from the YAML configuration file.

    Key (str): The source path specified in the configuration file.
    Value (EntryValue | None): The destination and policy for the source path,
        or None if not specified.
    """

    root: dict[str, EntryValue | None]

    def __getitem__(self, key: str) -> EntryValue | None:
        return self.root[key]


class LoadedVariables(RootModel):
    """Key-value pairs loaded from the YAML variables file.

    Key (str): The variable name specified in the variables file.
    Value (str): The value of the variable.
    """

    root: dict[str, str]

    def __getitem__(self, key: str) -> str:
        return self.root[key]
