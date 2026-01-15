from typing import TYPE_CHECKING

from recnys.backend.task import CanonicalSyncTask, canonicalize_sync_tasks

if TYPE_CHECKING:
    from collections.abc import Generator

    from recnys.frontend.task import SyncTask


def test_canonicalization(
    sync_tasks: list[SyncTask], canonical_sync_tasks: Generator[list[CanonicalSyncTask]]
) -> None:
    results = canonicalize_sync_tasks(sync_tasks)

    for result, expected in zip(results, canonical_sync_tasks, strict=True):
        assert result == expected
