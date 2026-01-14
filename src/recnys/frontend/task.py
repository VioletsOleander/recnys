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


class Dst:
    """Destination of file synchronization.

    Attributes:
        path (Path): The absolute path to the destination file or directory.
    """

    path: Path

    def __init__(
        self, linux: str | None = None, windows: str | None = None, src: Src | None = None
    ) -> None:
        """Initialize the destination path based on the current OS.

        If the path for the current OS is not provided, the dest path will be derived from
        the `src` argument. In this case, the `src` argument must be provided.

        If the path for the current OS is provided, it is used directly to derive the dest path.
        In this case, the `src` argument is optional.

        Current supported OS are Linux and Windows.

        Args:
            linux (str | None): Relative path for Linux systems.
            windows (str | None): Relative path for Windows systems.
            src (Src | None): Source object to derive default path if needed.
        """
        current_os = platform.system()
        match current_os:
            case "Linux":
                if linux is not None:
                    relative_path = linux
                elif src is None:
                    raise ValueError("src must be provided if dest is not specified")
                else:
                    # default to the same as src.path
                    relative_path = src.path
            case "Windows":
                if windows is not None:
                    relative_path = windows
                elif src is None:
                    raise ValueError("src must be provided if dest is not specified")
                else:
                    # default to "AppData/Roaming/" for directory src
                    # e.g. ".config/helix" -> "AppData/Roaming/helix"
                    relative_path = (
                        "AppData/Roaming/" / Path(*src.path.parts[1:]) if src.is_dir else src.path
                    )
            case _:
                raise NotImplementedError(f"Unsupported OS: {current_os}")

        self.path = Path.home() / relative_path

    def __str__(self) -> str:
        return str(self.path)


class Policy(StrEnum):
    """Policy for syncing files and directories.

    Attributes:
        OVERWRITE: Replace existing file/directory.
        SOURCE: Prepend a "source" line to the existing file.
    """

    OVERWRITE = "overwrite"
    SOURCE = "prepend a source statement"
