"""Provide `FileIOTask`."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["FileIOTask"]


@dataclass(frozen=True, kw_only=True)
class FileIOTask:
    """Representation of a file I/O task.

    Attributes:
        name (str): Name of the file I/O task, used for logging and record-keeping purposes.
        force_execute (bool): Whether to force execute the task, ignoring execution decisions.
        src (Path): Source path of the file I/O task.
        dst (Path): Destination path of the file I/O task.
    """

    name: str = field(default="File I/O Task", init=False)
    force_execute: bool = False
    src: Path
    dst: Path

    def __str__(self) -> str:
        return f"FileIOTask(name={self.name}, src={self.src}, dst={self.dst}, force_execute={self.force_execute})"
