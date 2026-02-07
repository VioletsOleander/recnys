from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from recnys.frontend.task import Dst, Policy, Src, SyncTask

from .constants import CONFIG_FILE_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

__all__ = ["init_filesystem", "make_sync_tasks"]


class _SrcAttr(NamedTuple):
    path: Path
    is_dir: bool


def _make_sync_task(
    src_attr: _SrcAttr,
    dst_path: Path | None,
    policy: Policy,
) -> SyncTask:
    """Create a SyncTask object by injecting given attributes."""
    src = object.__new__(Src)
    src.path = src_attr.path
    src.is_dir = src_attr.is_dir

    dst = object.__new__(Dst)
    dst.path = dst_path

    return SyncTask(src=src, dst=dst, policy=policy)


def _make_src_attrs_and_policies() -> tuple[tuple[_SrcAttr, Policy], ...]:
    return (
        (_SrcAttr(path=Path.cwd() / ".vimrc", is_dir=False), Policy.OVERWRITE),
        (_SrcAttr(path=Path.cwd() / ".bashrc", is_dir=False), Policy.SOURCE),
        (_SrcAttr(path=Path.cwd() / ".gitconfig", is_dir=False), Policy.OVERWRITE),
        (_SrcAttr(path=Path.cwd() / "nvim/", is_dir=True), Policy.OVERWRITE),
        (_SrcAttr(path=Path.cwd() / "yazi/", is_dir=True), Policy.OVERWRITE),
        (_SrcAttr(path=Path.cwd() / "nushell/", is_dir=True), Policy.OVERWRITE),
    )


def _make_dst_paths(system: str) -> tuple[Path | None, ...]:
    match system:
        case "Windows":
            return (
                Path.home() / "_vimrc",
                None,
                Path.home() / ".gitconfig",
                Path.home() / "AppData/Local/nvim",
                Path.home() / "AppData/Roaming/yazi",
                Path.home() / "AppData/Roaming/nushell",
            )
        case "Linux":
            return (
                Path.home() / ".vimrc",
                Path.home() / ".bashrc",
                Path.home() / ".gitconfig",
                Path.home() / ".config/nvim",
                Path.home() / ".config/yazi",
                Path.home() / ".config/nushell",
            )
        case _:
            raise ValueError(f"Unsupported system: {system}")


def make_sync_tasks(system: str) -> list[SyncTask]:
    """Construct the expected SyncTask objects.

    This function should be called after the fake filesystem is set up.
    """
    src_attrs_and_policies = _make_src_attrs_and_policies()
    dst_paths = _make_dst_paths(system)

    return [
        _make_sync_task(src_attr, dst_path, policy)
        for (src_attr, policy), dst_path in zip(src_attrs_and_policies, dst_paths, strict=True)
    ]


def init_filesystem(filesystem: FakeFilesystem, file_path: Path) -> FakeFilesystem:
    """Initialize the fake filesystem with a config file at the given path."""
    filesystem.create_file(file_path, contents=CONFIG_FILE_CONTENT)
    return filesystem
