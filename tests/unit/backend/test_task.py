from typing import TYPE_CHECKING

import pytest

from recnys.backend.task import canonicalize_sync_tasks
from recnys.testing.backend.constants import PARSED_SYNC_TASKS

if TYPE_CHECKING:
    from recnys.backend.task import CanonicalSyncTask
    from recnys.frontend.task import SyncTask


@pytest.fixture
def parsed_sync_tasks() -> list[SyncTask]:
    return PARSED_SYNC_TASKS


@pytest.mark.usefixtures("filesystem")
def test_canonicalization(
    parsed_sync_tasks: list[SyncTask], canonicalized_sync_tasks: list[CanonicalSyncTask]
) -> None:
    results = canonicalize_sync_tasks(parsed_sync_tasks)
    for result, expected in zip(
        sorted(results, key=lambda x: x.src),
        sorted(canonicalized_sync_tasks, key=lambda x: x.src),
        strict=True,
    ):
        assert result == expected
