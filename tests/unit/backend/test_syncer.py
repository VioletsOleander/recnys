from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncState
from recnys.frontend.task import Policy
from recnys.testing.backend.utils import make_syncer

if TYPE_CHECKING:
    from recnys.backend.task import CanonicalSyncTask


@pytest.fixture
def sync_state() -> SyncState:
    return SyncState()


@pytest.mark.usefixtures("filesystem")
def test_syncer(sync_state: SyncState, canonicalized_sync_tasks: list[CanonicalSyncTask]) -> None:
    syncer = make_syncer(state=sync_state, tasks=canonicalized_sync_tasks)
    syncer.sync(force=True)

    for task in canonicalized_sync_tasks:
        assert task.dst.exists()
        with task.src.open("r") as src_file, task.dst.open("r") as dst_file:
            if task.policy == Policy.OVERWRITE:
                assert src_file.read() == dst_file.read()
            elif task.policy == Policy.SOURCE:
                assert dst_file.read().strip() == f'source "{task.src}"'
