from typing import TYPE_CHECKING

import pytest

from recnys.testing.backend.constants import CANONICALIZED_SYNC_TASKS

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.backend.task import CanonicalSyncTask


@pytest.fixture
def canonicalized_sync_tasks() -> list[CanonicalSyncTask]:
    return CANONICALIZED_SYNC_TASKS


@pytest.fixture
def filesystem(
    filesystem: FakeFilesystem, canonicalized_sync_tasks: list[CanonicalSyncTask]
) -> FakeFilesystem:
    for task in canonicalized_sync_tasks:
        source_file = task.src
        filesystem.create_file(file_path=source_file, contents="dummy content")
    return filesystem
