from typing import TYPE_CHECKING

import pytest

from recnys.frontend.parse import parse
from recnys.testing.frontend.utils import make_parsed_sync_tasks

if TYPE_CHECKING:
    from recnys.frontend.load import LoadedConfig
    from recnys.frontend.task import SyncTask


@pytest.fixture
def parsed_sync_tasks(system: str) -> list[SyncTask]:
    return make_parsed_sync_tasks(system)


@pytest.mark.usefixtures("filesystem")
def test_parse(loaded_config: LoadedConfig, parsed_sync_tasks: list[SyncTask]) -> None:
    sync_tasks = parse(loaded_config)
    for result_task, expected_task in zip(sync_tasks, parsed_sync_tasks, strict=True):
        assert result_task == expected_task
