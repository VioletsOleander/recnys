from pathlib import Path

from recnys.backend.task import CanonicalSyncTask
from recnys.frontend.task import Policy
from recnys.testing.frontend.utils import SrcAttr, SyncTaskAttr, make_sync_task

__all__ = [
    "CANONICALIZED_SYNC_TASKS",
    "DST_CONTENT",
    "FILES_UNDER_DIR",
    "PARSED_SYNC_TASKS",
    "SRC_CONTENT",
]

SRC_CONTENT = "Sample content for source files."
DST_CONTENT = "Sample content for destination files."

_SYNC_TASK_ATTRS = (
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/file"), is_dir=False),
        dst=Path("/destination/file"),
        policy=Policy.SOURCE,
    ),
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/file"), is_dir=False),
        dst=Path("/destination/file"),
        policy=Policy.OVERWRITE,
    ),
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/file_no_sync"), is_dir=False),
        dst=None,
        policy=Policy.SOURCE,
    ),
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/dir/"), is_dir=True),
        dst=Path("/destination/dir/"),
        policy=Policy.OVERWRITE,
    ),
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/dir_no_sync/"), is_dir=True),
        dst=None,
        policy=Policy.SOURCE,
    ),
    SyncTaskAttr(
        src=SrcAttr(path=Path("/source/dir/file1.txt"), is_dir=False),
        dst=Path("/destination/dir/file1.txt"),
        policy=Policy.SOURCE,
    ),
)

PARSED_SYNC_TASKS = [make_sync_task(sync_task_attr=attr) for attr in _SYNC_TASK_ATTRS]

FILES_UNDER_DIR = (
    Path("/source/dir/file1.txt"),
    Path("/source/dir/file2.txt"),
    Path("/source/dir/subdir/file3.txt"),
)


def _canonicalized_sync_tasks() -> list[CanonicalSyncTask]:
    tasks: dict[Path, CanonicalSyncTask] = {}

    for src, dst, policy in _SYNC_TASK_ATTRS:
        if dst is None:
            continue

        if not src.is_dir:
            tasks[src.path] = CanonicalSyncTask(src.path, dst, policy)
        else:
            for file_path in FILES_UNDER_DIR:
                relative_path = file_path.relative_to(src.path)
                effective_dst_path = dst / relative_path
                tasks[file_path] = CanonicalSyncTask(file_path, effective_dst_path, policy)

    return list(tasks.values())


CANONICALIZED_SYNC_TASKS = _canonicalized_sync_tasks()
