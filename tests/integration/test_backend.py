from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncState
from recnys.backend.task import canonicalize_sync_tasks
from recnys.frontend.task import Policy
from recnys.testing.backend.constants import CANONICALIZED_SYNC_TASKS, PARSED_SYNC_TASKS
from recnys.testing.backend.utils import make_syncer

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.backend.task import CanonicalSyncTask
    from recnys.frontend.task import SyncTask


@pytest.fixture
def parsed_sync_tasks() -> list[SyncTask]:
    return PARSED_SYNC_TASKS


@pytest.fixture
def sync_state() -> SyncState:
    return SyncState()


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


@pytest.mark.usefixtures("filesystem")
def test_backend(sync_state: SyncState, parsed_sync_tasks: list[SyncTask]) -> None:
    tasks = canonicalize_sync_tasks(parsed_sync_tasks)

    syncer = make_syncer(state=sync_state, tasks=tasks)
    syncer.sync(force=True)

    for task in tasks:
        assert task.dst.exists()
        with task.src.open("r") as src_file, task.dst.open("r") as dst_file:
            if task.policy == Policy.OVERWRITE:
                assert src_file.read() == dst_file.read()
            elif task.policy == Policy.SOURCE:
                assert dst_file.read().strip() == f'source "{task.src}"'
