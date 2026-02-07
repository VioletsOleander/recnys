from pathlib import Path
from typing import TYPE_CHECKING

from recnys.backend.state import SyncState
from recnys.backend.syncer import Syncer
from recnys.frontend.load import load
from recnys.frontend.parse import parse
from recnys.testing.backend.arranger import init_filesystem as init_fs_backend
from recnys.testing.backend.arranger import make_canonical_sync_tasks
from recnys.testing.backend.asserter import sync_test
from recnys.testing.frontend.arranger import init_filesystem as init_fs_frontend

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_integration(filesystem: FakeFilesystem, system: str) -> None:
    file_path = Path.home() / Path("recnys.yaml")
    init_fs_frontend(filesystem=filesystem, file_path=file_path)
    expected_canonical_sync_tasks = make_canonical_sync_tasks(system)
    init_fs_backend(filesystem=filesystem, canonical_sync_tasks=expected_canonical_sync_tasks)

    # load
    config = load(file_path=file_path)

    # parse
    tasks = parse(config)

    # canonicalize and sync
    state = SyncState.from_json(Path(".sync_states.json"))
    syncer = Syncer(sync_state=state, sync_tasks=tasks)
    syncer.sync(force=True)

    sync_test(canonical_sync_tasks=expected_canonical_sync_tasks)
