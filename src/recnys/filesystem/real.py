from typing import TYPE_CHECKING, override

from .interface import FileSystem

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["RealFlieSystem"]


class RealFlieSystem(FileSystem):
    @override
    def exists(self, p: Path, *, follow_symlinks: bool = True) -> bool:
        return p.exists(follow_symlinks=follow_symlinks)

    @override
    def rmdir(self, p: Path) -> None:
        p.rmdir()

    @override
    def unlink(self, p: Path, *, missing_ok: bool = False) -> None:
        p.unlink(missing_ok=missing_ok)

    @override
    def mkdir(self, p: Path) -> None:
        p.mkdir()

    @override
    def write_text(self, p: Path, text: str) -> None:
        try:
            tmp = p.with_suffix(f"{p.suffix}.recnys.tmp")
            tmp.write_text(text, encoding="utf-8")
            tmp.replace(p)
        finally:
            tmp.unlink(missing_ok=True)

    @override
    def symlink_to(self, src: Path, dst: Path) -> None:
        src.symlink_to(dst)
