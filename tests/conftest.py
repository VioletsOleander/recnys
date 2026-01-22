from typing import TYPE_CHECKING

import pytest

from recnys.backend.task import CanonicalSyncTask
from recnys.testing.frontend.constants import LOADED_CONFIG, PARSED_SYNC_TASKS

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

    from recnys.frontend.load import LoadedConfig
    from recnys.frontend.task import SyncTask


@pytest.fixture(params=["Linux", "Windows"])
def platform(mocker: MockerFixture, request: pytest.FixtureRequest) -> Mock:
    return mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)


@pytest.fixture
def loaded_config() -> LoadedConfig:
    return LOADED_CONFIG


@pytest.fixture
def parsed_sync_tasks(platform: Mock) -> list[SyncTask]:
    return PARSED_SYNC_TASKS[platform.return_value]


@pytest.fixture
def canonical_sync_tasks(platform: Mock) -> Generator[list[CanonicalSyncTask]]:
    from recnys.testing.backend.constants import DST_PATHS, POLICIES, SRC_PATHS  # noqa: PLC0415

    curr_os = platform.return_value
    for src_path in SRC_PATHS[curr_os]:
        src_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.touch()

    yield [
        CanonicalSyncTask(src=src_path, dst=dst_path, policy=policy)
        for src_path, dst_path, policy in zip(
            SRC_PATHS[curr_os], DST_PATHS[curr_os], POLICIES[curr_os], strict=True
        )
    ]

    for src_path in SRC_PATHS[curr_os]:
        src_path.unlink()
