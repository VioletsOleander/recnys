from typing import TYPE_CHECKING

import pytest

from recnys.testing.frontend.constants import LOADED_CONFIG, PARSED_SYNC_TASKS

if TYPE_CHECKING:
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
