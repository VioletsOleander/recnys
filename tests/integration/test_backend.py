from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncState
from recnys.backend.task import canonicalize_sync_tasks
from recnys.testing.backend.constants import CANONICALIZED_SYNC_TASKS, PARSED_SYNC_TASKS
from recnys.testing.backend.utils import make_syncer, prepare_filesystem, sync_test

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
    return prepare_filesystem(
        filesystem=filesystem, canonicalized_sync_tasks=canonicalized_sync_tasks
    )


@pytest.mark.usefixtures("filesystem")
def test_backend(sync_state: SyncState, parsed_sync_tasks: list[SyncTask]) -> None:
    tasks = canonicalize_sync_tasks(parsed_sync_tasks)

    syncer = make_syncer(state=sync_state, tasks=tasks)
    syncer.sync(force=True)

    sync_test(canonicalized_sync_tasks=tasks)
