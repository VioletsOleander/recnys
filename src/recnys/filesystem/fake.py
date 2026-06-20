from pathlib import Path
from typing import override

from .interface import FileSystem


class FakeFileSystem(FileSystem):
    """An overlay on top of the real filesystem."""

    deleted: list[Path]
    created: list[Path]

    def __init__(self) -> None:
        self.deleted = []
        self.created = []

    @override
    def exists(self, p: Path, *, follow_symlinks: bool = True) -> bool:
        if p in self.created:
            return True

        if p in self.deleted:
            return False

        return p.exists(follow_symlinks=follow_symlinks)

    @override
    def rmdir(self, p: Path) -> None:
        if p not in self.deleted:
            self.deleted.append(p)
        else:
            raise FileNotFoundError(f"Path {p} is already deleted")

    @override
    def unlink(self, p: Path, *, missing_ok: bool = False) -> None:
        if p not in self.deleted:
            self.deleted.append(p)
        elif not missing_ok:
            raise FileNotFoundError(f"Path {p} is already deleted")

    @override
    def mkdir(self, p: Path) -> None:
        return

    @override
    def write_text(self, p: Path, text: str) -> None:
        return

    @override
    def symlink_to(self, src: Path, dst: Path) -> None:
        src.symlink_to(dst)

    def _is_empty_dir(p: Path) -> bool:
        if not dst.is_dir(follow_symlinks=False):
            raise RuntimeError(
                f"Path {dst} is occupied, failed to remove the directory.\n"
                "Hint: Please remove the file or symbolic link at the path."
            )

    if next(dst.iterdir(), None) is not None:
        return logger.debug("Directory %s is not empty, skip removing it", dst)
