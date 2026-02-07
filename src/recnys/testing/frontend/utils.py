"""Provide `make_parsed_sync_tasks` to defer the construction of expected SyncTask objects after fake filesystem is set up."""

from pathlib import Path
from typing import NamedTuple

from recnys.frontend.task import Dst, Policy, Src, SyncTask

__all__ = ["make_parsed_sync_tasks"]


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
        (_SrcAttr(path=Path.cwd() / "nushell/config.nu", is_dir=False), Policy.OVERWRITE),
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
                Path.home() / "AppData/Roaming/nushell/config.nu",
            )
        case "Linux":
            return (
                Path.home() / ".vimrc",
                Path.home() / ".bashrc",
                Path.home() / ".gitconfig",
                Path.home() / ".config/nvim",
                Path.home() / ".config/yazi",
                Path.home() / ".config/nushell",
                Path.home() / ".config/nushell/config.nu",
            )
        case _:
            raise ValueError(f"Unsupported system: {system}")


def make_parsed_sync_tasks(system: str) -> list[SyncTask]:
    src_attrs_and_policies = _make_src_attrs_and_policies()
    dst_paths = _make_dst_paths(system)

    return [
        _make_sync_task(src_attr, dst_path, policy)
        for (src_attr, policy), dst_path in zip(src_attrs_and_policies, dst_paths, strict=True)
    ]
