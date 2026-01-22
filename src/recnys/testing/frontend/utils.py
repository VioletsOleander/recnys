from typing import TYPE_CHECKING, NamedTuple

from recnys.frontend.task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["SrcAttr", "make_sync_task"]


class SrcAttr(NamedTuple):
    path: Path
    is_dir: bool


def make_sync_task(src_attr: SrcAttr, dst_path: Path | None, policy: Policy) -> SyncTask:
    """Create custom SyncTask by injecting given parameters."""
    src = object.__new__(Src)
    src.path = src_attr.path
    src.is_dir = src_attr.is_dir

    dst = object.__new__(Dst)
    dst.path = dst_path

    return SyncTask(src=src, dst=dst, policy=policy)
