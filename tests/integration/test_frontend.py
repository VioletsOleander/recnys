from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.frontend.load import load
from recnys.frontend.parse import parse
from recnys.testing.frontend.constants import CONFIG_FILE_CONTENT, LOADED_CONFIG
from recnys.testing.frontend.arranger import make_sync_tasks

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.frontend.load import LoadedConfig


@pytest.fixture
def loaded_config() -> LoadedConfig:
    return LOADED_CONFIG


def test_frontend(filesystem: FakeFilesystem, system: str) -> None:
    # load
    filesystem.create_file("/recnys.yaml", contents=CONFIG_FILE_CONTENT)
    config = load(Path("/recnys.yaml"))

    # parse
    result_sync_tasks = parse(config)
    expected_sync_tasks = make_sync_tasks(system)
    for result_task, expected_task in zip(result_sync_tasks, expected_sync_tasks, strict=True):
        assert result_task == expected_task
