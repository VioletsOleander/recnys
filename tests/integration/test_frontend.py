from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.frontend.load import load
from recnys.frontend.parse import parse
from recnys.testing.frontend.constants import CONFIG_FILE_CONTENT, LOADED_CONFIG
from recnys.testing.frontend.utils import make_parsed_sync_tasks

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.frontend.load import LoadedConfig
    from recnys.frontend.task import SyncTask


@pytest.fixture
def loaded_config() -> LoadedConfig:
    return LOADED_CONFIG


@pytest.fixture
def parsed_sync_tasks(loaded_config: LoadedConfig, system: str) -> list[SyncTask]:
    return make_parsed_sync_tasks(loaded_config, system)


def test_frontend(filesystem: FakeFilesystem, parsed_sync_tasks: list[SyncTask]) -> None:
    # load
    filesystem.create_file("/recnys.yaml", contents=CONFIG_FILE_CONTENT)
    config = load(Path("/recnys.yaml"))
    # parse
    sync_tasks = parse(config)
    for result_task, expected_task in zip(sync_tasks, parsed_sync_tasks, strict=True):
        assert result_task == expected_task
