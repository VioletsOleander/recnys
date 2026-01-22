from typing import TYPE_CHECKING

from recnys.backend.syncer import Syncer

if TYPE_CHECKING:
    from recnys.backend.state import SyncState
    from recnys.backend.task import CanonicalSyncTask

__all__ = ["make_syncer"]


def make_syncer(state: SyncState, tasks: list[CanonicalSyncTask]) -> Syncer:
    """Make Syncer instance by injecting sync states and tasks."""
    syncer = object.__new__(Syncer)
    syncer.sync_state = state
    syncer.sync_tasks = tasks
    return syncer
