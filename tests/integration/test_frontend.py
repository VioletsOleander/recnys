from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.frontend.load import load
from recnys.frontend.parse import parse
from recnys.frontend.task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from pytest_mock import MockerFixture

IN_FILE = Path(__file__).parent / "frontend.in.yaml"

SRC_PARAMS = [
    (Path(".vimrc"), False),
    (Path(".bashrc"), False),
    (Path(".inputrc"), False),
    (Path(".tmux.conf"), False),
    (Path(".gitconfig"), False),
    (Path(".config/nvim/"), True),
    (Path(".config/helix/"), True),
    (Path(".config/yazi/"), True),
]
SRC_PARAMS = [(Path.cwd() / p, is_dir) for p, is_dir in SRC_PARAMS]

DST_PARAMS_LINUX = [
    Path("~/.vimrc"),
    Path("~/.bashrc"),
    Path("~/.inputrc"),
    Path("~/.tmux.conf"),
    Path("~/.gitconfig"),
    Path("~/.config/nvim"),
    Path("~/.config/helix"),
    Path("~/.config/yazi"),
]
DST_PARAMS_LINUX = [p.expanduser() for p in DST_PARAMS_LINUX]

DST_PARAMS_WINDOWS = [
    Path("~/_vimrc"),
    None,
    None,
    None,
    Path("~/.gitconfig"),
    Path("~/AppData/Local/nvim"),
    Path("~/AppData/Roaming/helix"),
    Path("~/AppData/Roaming/yazi"),
]
DST_PARAMS_WINDOWS = [p.expanduser() if p is not None else None for p in DST_PARAMS_WINDOWS]
DST_PARAMS = {
    "Linux": DST_PARAMS_LINUX,
    "Windows": DST_PARAMS_WINDOWS,
}

POLICIES = [Policy.OVERWRITE for _ in SRC_PARAMS]
POLICIES[1] = Policy.SOURCE


class TestFrontEnd:
    @pytest.fixture(params=["Linux", "Windows"])
    def platform(self, mocker: MockerFixture, request: pytest.FixtureRequest) -> str:
        mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)
        return request.param

    @pytest.fixture
    def expected_tasks(self, platform: str) -> list[SyncTask]:
        tasks = []

        for (src_path, src_is_dir), dst_path, policy in zip(
            SRC_PARAMS, DST_PARAMS[platform], POLICIES, strict=True
        ):
            src = object.__new__(Src)
            src.path = src_path
            src.is_dir = src_is_dir

            dst = object.__new__(Dst)
            dst.path = dst_path

            tasks.append(SyncTask(src=src, dst=dst, policy=policy))

        return tasks

    def test_frontend(self, expected_tasks: list[SyncTask]) -> None:
        # load
        loaded_config = load(IN_FILE)
        for k, v in loaded_config.items():
            assert isinstance(k, str)
            assert v is None or isinstance(v, dict)

        # parse
        sync_tasks = parse(loaded_config)
        for task, expected_task in zip(sync_tasks, expected_tasks, strict=True):
            assert task == expected_task
