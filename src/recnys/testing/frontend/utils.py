from typing import TYPE_CHECKING

from recnys.frontend.task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["make_sync_task"]


def make_sync_task(src_path: Path, src_is_dir: bool, dst_path: Path, policy: Policy) -> SyncTask:  # noqa: FBT001
    """Create custom SyncTask by injecting given parameters."""
    src = object.__new__(Src)
    src.path = src_path
    src.is_dir = src_is_dir

    dst = object.__new__(Dst)
    dst.path = dst_path

    return SyncTask(src=src, dst=dst, policy=policy)
