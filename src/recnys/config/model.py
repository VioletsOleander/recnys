"""Provide data models for loaded configuration and variables."""

from typing import Literal

from pydantic import BaseModel, RootModel

__all__ = ["LoadedConfig", "LoadedVariables"]


class _Dest(BaseModel):
    Linux: str | None = None
    Windows: str | None = None


class _EntryValue(BaseModel):
    dest: _Dest | None = None
    policy: Literal["copy", "symlink"] | None = None


class LoadedConfig(RootModel):
    root: dict[str, _EntryValue | None]

    def __getitem__(self, key: str) -> _EntryValue | None:
        return self.root[key]


class LoadedVariables(RootModel):
    root: dict[str, str]

    def __getitem__(self, key: str) -> str:
        return self.root[key]
