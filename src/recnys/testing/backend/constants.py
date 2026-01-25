from pathlib import Path

from recnys.backend.task import CanonicalSyncTask
from recnys.frontend.task import Policy
from recnys.testing.frontend.utils import SrcAttr, make_sync_task

__all__ = [
    "CANONICALIZED_SYNC_TASKS",
    "DST_CONTENT",
    "FILES_UNDER_DIR",
    "PARSED_SYNC_TASKS",
    "SRC_CONTENT",
]

SRC_CONTENT = "Sample content for source files."
DST_CONTENT = "Sample content for destination files."

_SRC_ATTRS = (
    SrcAttr(path=Path("/source/file_with_dest"), is_dir=False),
    SrcAttr(path=Path("/source/file_without_dest"), is_dir=False),
    SrcAttr(path=Path("/source/dir_with_dest/"), is_dir=True),
    SrcAttr(path=Path("/source/dir_without_dest/"), is_dir=True),
)

_DST_PATHS = (
    Path("/destination/file_with_dest"),
    None,
    Path("/destination/dir_with_dest/"),
    None,
)

_POLICIES = (
    Policy.OVERWRITE,
    Policy.DEFAULT,
    Policy.SOURCE,
    Policy.DEFAULT,
)

PARSED_SYNC_TASKS = [
    make_sync_task(src_attr, dst_path, policy)
    for src_attr, dst_path, policy in zip(_SRC_ATTRS, _DST_PATHS, _POLICIES, strict=True)
]

FILES_UNDER_DIR = (
    Path("/source/dir_with_dest/file1.txt"),
    Path("/source/dir_with_dest/file2.txt"),
    Path("/source/dir_with_dest/subdir/file3.txt"),
)


def _canonicalized_sync_tasks() -> list[CanonicalSyncTask]:
    tasks = []
    for src_attr, dst_path, policy in zip(_SRC_ATTRS, _DST_PATHS, _POLICIES, strict=True):
        if not src_attr.is_dir:
            if dst_path is None:
                continue
            tasks.append(CanonicalSyncTask(src_attr.path, dst_path, policy))
        else:
            if dst_path is None:
                continue
            for file_path in FILES_UNDER_DIR:
                relative_path = file_path.relative_to(src_attr.path)
                effective_dst_path = dst_path / relative_path
                tasks.append(CanonicalSyncTask(file_path, effective_dst_path, policy))

    return tasks


CANONICALIZED_SYNC_TASKS = _canonicalized_sync_tasks()
