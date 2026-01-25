from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncState
from recnys.testing.backend.utils import make_syncer, sync_test

if TYPE_CHECKING:
    from recnys.backend.task import CanonicalSyncTask


@pytest.fixture
def sync_state() -> SyncState:
    return SyncState()


@pytest.mark.usefixtures("filesystem")
def test_syncer(sync_state: SyncState, canonicalized_sync_tasks: list[CanonicalSyncTask]) -> None:
    syncer = make_syncer(state=sync_state, tasks=canonicalized_sync_tasks)
    syncer.sync(force=True)
    sync_test(canonicalized_sync_tasks=canonicalized_sync_tasks)
