from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.io.record import ExecutionRecord
from recnys.sync.syncer import FileSyncer, FileSyncTask
from recnys.testing.render.constants import RENDERED_CONTENT

from .constants import NORMAL_FILE_CONTENT, LazyConstants

__all__ = ["create_source_files", "make_sync_record", "make_syncer"]


def create_source_files(filesystem: FakeFilesystem, tasks: list[FileSyncTask]) -> None:
    for task in tasks:
        file_path = task.src
        content = (
            RENDERED_CONTENT
            if task.src.is_relative_to(LazyConstants.rendered_file_dir)
            else NORMAL_FILE_CONTENT
        )
        filesystem.create_file(file_path=file_path, contents=content)


def make_sync_record() -> ExecutionRecord:
    """Construct and return an empty ExecutionRecord for syncing.

    This function should be called after the fake filesystem is set up.
    """
    return ExecutionRecord.from_json(file_path=LazyConstants.record_file_path)


def make_syncer() -> FileSyncer:
    """Construct and return a FileSyncer.

    This function should be called after the fake filesystem is set up.
    """
    return FileSyncer(skip=True)
