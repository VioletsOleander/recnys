from typing import TYPE_CHECKING

import pytest

from recnys.backend.task import canonicalize_sync_tasks

if TYPE_CHECKING:
    from recnys.backend.task import CanonicalSyncTask
    from recnys.frontend.task import SyncTask


@pytest.mark.usefixtures("fake_fs")
def test_canonicalization(
    parsed_sync_tasks: list[SyncTask], canonicalized_sync_tasks: list[CanonicalSyncTask]
) -> None:
    results = canonicalize_sync_tasks(parsed_sync_tasks)
    for result, expected in zip(results, canonicalized_sync_tasks, strict=True):
        assert result == expected
