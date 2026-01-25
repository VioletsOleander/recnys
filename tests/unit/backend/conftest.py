from typing import TYPE_CHECKING

import pytest

from recnys.testing.backend.constants import CANONICALIZED_SYNC_TASKS
from recnys.testing.backend.utils import prepare_filesystem

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.backend.task import CanonicalSyncTask


@pytest.fixture
def canonicalized_sync_tasks() -> list[CanonicalSyncTask]:
    return CANONICALIZED_SYNC_TASKS


@pytest.fixture
def filesystem(
    filesystem: FakeFilesystem, canonicalized_sync_tasks: list[CanonicalSyncTask]
) -> FakeFilesystem:
    return prepare_filesystem(
        filesystem=filesystem, canonicalized_sync_tasks=canonicalized_sync_tasks
    )
