from pathlib import Path
from typing import TYPE_CHECKING

from .constants import (
    DEST_FILES_LINUX,
    DEST_FILES_WINDOWS,
    POLICIES_LINUX,
    POLICIES_WINDOWS,
    SOURCE_FILES_LINUX,
    SOURCE_FILES_WINDOWS,
)

if TYPE_CHECKING:
    from recnys.frontend.task import Policy

__all__ = ["make_dest_files", "make_policies", "make_source_files"]


def make_source_files(system: str) -> list[Path]:
    match system:
        case "Linux":
            source_files = SOURCE_FILES_LINUX
        case "Windows":
            source_files = SOURCE_FILES_WINDOWS
        case _:
            raise ValueError(f"Unsupported system: {system}")

    return [Path.cwd() / f for f in source_files]


def make_dest_files(system: str) -> list[Path]:
    match system:
        case "Linux":
            dest_files = DEST_FILES_LINUX
        case "Windows":
            dest_files = DEST_FILES_WINDOWS
        case _:
            raise ValueError(f"Unsupported system: {system}")

    return [Path.home() / f for f in dest_files]


def make_policies(system: str) -> list[Policy]:
    match system:
        case "Linux":
            policies = POLICIES_LINUX
        case "Windows":
            policies = POLICIES_WINDOWS
        case _:
            raise ValueError(f"Unsupported system: {system}")

    return list(policies)
