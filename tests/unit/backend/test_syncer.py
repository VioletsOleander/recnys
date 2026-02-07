from typing import TYPE_CHECKING

from recnys.backend.state import SyncState
from recnys.testing.backend.arranger import init_filesystem, make_canonical_sync_tasks, make_syncer
from recnys.testing.backend.asserter import sync_test

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_syncer(filesystem: FakeFilesystem, system: str) -> None:
    canonical_sync_tasks = make_canonical_sync_tasks(system)
    syncer = make_syncer(state=SyncState(), tasks=canonical_sync_tasks)
    init_filesystem(filesystem=filesystem, canonical_sync_tasks=canonical_sync_tasks)

    syncer.sync(force=True)

    sync_test(canonical_sync_tasks=canonical_sync_tasks)
