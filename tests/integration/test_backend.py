from typing import TYPE_CHECKING

from recnys.backend.state import SyncState
from recnys.backend.task import canonicalize_sync_tasks
from recnys.testing.backend.arranger import init_filesystem, make_canonical_sync_tasks, make_syncer
from recnys.testing.backend.asserter import sync_test
from recnys.testing.frontend.arranger import make_sync_tasks

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_backend(filesystem: FakeFilesystem, system: str) -> None:
    expected_canonical_sync_tasks = make_canonical_sync_tasks(system)
    init_filesystem(filesystem=filesystem, canonical_sync_tasks=expected_canonical_sync_tasks)

    # canonicalization
    parsed_sync_tasks = make_sync_tasks(system)
    canonical_sync_tasks = canonicalize_sync_tasks(parsed_sync_tasks)

    # sync
    syncer = make_syncer(state=SyncState(), tasks=canonical_sync_tasks)
    syncer.sync(force=True)

    sync_test(canonical_sync_tasks=expected_canonical_sync_tasks)
