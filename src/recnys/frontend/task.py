"""Define `SyncTask` and related data structures for describing synchronization tasks."""

import platform
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

__all__ = ["Dst", "Policy", "Src", "SyncTask"]


@dataclass(frozen=True)
class SyncTask:
    """Description of a synchronization task.

    Attributes:
        src (Src): Source of the synchronization.
        dst (Dst): Destination of the synchronization.
        policy (Policy): Policy of the synchronization.
    """

    src: Src
    dst: Dst
    policy: Policy

    def __str__(self) -> str:
        return f"SyncTask(src={self.src}, dst={self.dst}, policy={self.policy})"


class Src:
    """Source of file synchronization.

    Attributes:
        path (Path): The absolute path to the source file or directory.
        is_dir (bool): Whether the source is a directory.
    """

    path: Path
    is_dir: bool

    def __init__(self, path: str) -> None:
        """Resolve source path relative to the current working directory."""
        self.is_dir = path.endswith("/")
        self.path = Path.cwd() / path

    def __str__(self) -> str:
        return str(self.path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Src):
            return NotImplemented
        return self.path == other.path and self.is_dir == other.is_dir

    def __hash__(self) -> int:
        return hash((self.path, self.is_dir))


class Dst:
    """Destination of file synchronization.

    Attributes:
        path (Path | None): The absolute path to the destination file or directory, or
            None if not specified.
    """

    path: Path | None

    def __init__(self, src: str, linux: str | None = None, windows: str | None = None) -> None:
        """Initialize the destination path based on the current OS.

        If the path for the current OS is not provided, the dest path will be derived from
        the `src` argument. In this case, the `src` argument must be provided.

        If the path for the current OS is provided, it is used directly to derive the dest path.

        Current supported OS are Linux and Windows.

        Args:
            src (str): Source path to derive destination from.
            linux (str | None): Relative path for Linux systems.
            windows (str | None): Relative path for Windows systems.
        """
        current_os = platform.system()
        match current_os:
            case "Windows":
                if windows is None:
                    if src.endswith("/"):
                        relative_path = "AppData/Roaming/" + src.removeprefix(".config/")
                    else:
                        relative_path = src
                else:
                    relative_path = windows
            case "Linux":
                relative_path = src if linux is None else linux
            case _:
                raise NotImplementedError(f"Unsupported OS: {current_os}")

        if relative_path == "":
            self.path = None
        else:
            self.path = Path.home() / relative_path

    def __str__(self) -> str:
        return str(self.path)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dst):
            return NotImplemented
        return self.path == other.path

    def __hash__(self) -> int:
        return hash(self.path)


class Policy(StrEnum):
    """Policy for syncing files and directories.

    Attributes:
        OVERWRITE: Replace existing file/directory.
        SOURCE: Prepend a "source" line to the existing file.
    """

    OVERWRITE = "overwrite"
    SOURCE = "prepend a source statement"
