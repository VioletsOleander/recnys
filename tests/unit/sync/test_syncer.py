from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.testing.build.arrange import make_sync_tasks
from recnys.testing.sync.arrange import create_source_files, make_sync_record, make_syncer
from recnys.testing.sync.asserting import assert_sync_record_io, assert_synced_correctly


def test_sync(system: str, filesystem: FakeFilesystem) -> None:
    sync_tasks = make_sync_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    record = make_sync_record()
    syncer = make_syncer()

    record = syncer.sync(tasks=sync_tasks, last_record=record)

    assert_synced_correctly(tasks=sync_tasks)
    assert_sync_record_io(sync_record=record)
