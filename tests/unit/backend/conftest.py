from typing import TYPE_CHECKING

import pytest

from recnys.testing.backend.constants import (
    CANONICALIZED_SYNC_TASKS,
    FILES_UNDER_DIR,
    PARSED_SYNC_TASKS,
)

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFileSystem

    from recnys.backend.task import CanonicalSyncTask
    from recnys.frontend.task import SyncTask


@pytest.fixture
def fake_fs(fs: FakeFileSystem) -> FakeFileSystem:
    for file_path in FILES_UNDER_DIR:
        fs.create_file(file_path)
    return fs


@pytest.fixture
def parsed_sync_tasks() -> list[SyncTask]:
    return PARSED_SYNC_TASKS


@pytest.fixture
def canonicalized_sync_tasks() -> list[CanonicalSyncTask]:
    return CANONICALIZED_SYNC_TASKS
