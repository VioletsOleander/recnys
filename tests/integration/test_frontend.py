from pathlib import Path
from typing import TYPE_CHECKING

from recnys.frontend.load import load
from recnys.frontend.parse import parse

if TYPE_CHECKING:
    from recnys.frontend.load import LoadedConfig
    from recnys.frontend.task import SyncTask


IN_FILE = Path(__file__).parent / "frontend.in.yaml"


def test_frontend(loaded_config: LoadedConfig, parsed_sync_tasks: list[SyncTask]) -> None:
    # load
    config = load(IN_FILE)
    assert config == loaded_config

    # parse
    sync_tasks = parse(loaded_config)
    for result_task, expected_task in zip(sync_tasks, parsed_sync_tasks, strict=True):
        assert result_task == expected_task
