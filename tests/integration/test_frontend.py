from pathlib import Path
from typing import TYPE_CHECKING

from recnys.frontend.load import load
from recnys.frontend.parse import parse

if TYPE_CHECKING:
    from recnys.frontend.task import SyncTask


IN_FILE = Path(__file__).parent / "frontend.in.yaml"


class TestFrontEnd:
    def test_frontend(self, sync_tasks: list[SyncTask]) -> None:
        expected_tasks = sync_tasks

        # load
        loaded_config = load(IN_FILE)
        for k, v in loaded_config.items():
            assert isinstance(k, str)
            assert v is None or isinstance(v, dict)

        # parse
        sync_tasks = parse(loaded_config)
        for task, expected_task in zip(sync_tasks, expected_tasks, strict=True):
            assert task == expected_task
