from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["FileSystem"]


class FileSystem(Protocol):
    """FileSystem provides filesystem modification and existance check operations."""

    @abstractmethod
    def exists(self, p: Path, *, follow_symlinks: bool = True) -> bool:
        """Return True if `p` exists in the filesystem, otherwise False.

        Args:
            p (Path): The path to check existance.
            follow_symlinks (bool): Specify False to check wheter a symlink exists.
        """

    @abstractmethod
    def rmdir(self, p: Path) -> None:
        """Remove empty directory `p`.

        Args:
            p (Path): The path to the directory to remove.
        """

    @abstractmethod
    def unlink(self, p: Path, *, missing_ok: bool = False) -> None:
        """Remove file or link `p`.

        Args:
            p (Path): The path to the file or link to remove.
            missing_ok (bool): Specify True to not raise error when `p` does not exist.
        """

    @abstractmethod
    def mkdir(self, p: Path) -> None:
        """Create new directory `p`."""

    @abstractmethod
    def write_text(self, p: Path, text: str) -> None:
        """Atomically write `text` to `p`."""

    @abstractmethod
    def symlink_to(self, src: Path, dst: Path) -> None:
        """Make `src` a symlink pointing to `dst`."""
