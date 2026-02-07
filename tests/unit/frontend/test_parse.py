from typing import TYPE_CHECKING

import pytest

from recnys.frontend.parse import parse
from recnys.testing.frontend.utils import make_sync_tasks

if TYPE_CHECKING:
    from recnys.frontend.load import LoadedConfig


@pytest.mark.usefixtures("filesystem")
def test_parse(loaded_config: LoadedConfig, system: str) -> None:
    result_sync_tasks = parse(loaded_config)
    expected_sync_tasks = make_sync_tasks(system)

    for result_task, expected_task in zip(result_sync_tasks, expected_sync_tasks, strict=True):
        assert result_task == expected_task
