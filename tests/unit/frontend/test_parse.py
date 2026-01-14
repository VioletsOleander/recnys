from typing import TYPE_CHECKING

import pytest

from recnys.frontend.parse import parse
from recnys.frontend.task import Policy

if TYPE_CHECKING:
    from unittest.mock import Mock
    from pytest_mock import MockerFixture

    from recnys.frontend.load import LoadedConfig

DEFAULT_POLICY = Policy.OVERWRITE


INPUT_CONFIGS = [
    {".vimrc": {"dest": {"windows": "_vimrc"}}},
    {".bashrc": {"dest": {"windows": ""}, "policy": "source"}},
    {".gitconfig": None},
    {".config/nvim/": {"dest": {"windows": "AppData/Local/nvim"}}},
    {".config/yazi/": None},
]

REFERENCE_CONFIGS = [
    {".vimrc": {"dest": {"linux": ".vimrc", "windows": "_vimrc"}, "policy": "overwrite"}},
    {".bashrc": {"dest": {"linux": ".bashrc", "windows": ""}, "policy": "source"}},
    {
        ".gitconfig": {
            "dest": {"linux": ".gitconfig", "windows": ".gitconfig"},
            "policy": "overwrite",
        }
    },
    {
        ".config/nvim/": {
            "dest": {"linux": ".config/nvim/", "windows": "AppData/Local/nvim"},
            "policy": "overwrite",
        }
    },
    {
        ".config/yazi/": {
            "dest": {"linux": ".config/yazi/", "windows": "AppData/Roaming/yazi"},
            "policy": "overwrite",
        }
    },
]


@pytest.fixture(params=["Linux", "Windows"])
def platform(mocker: MockerFixture, request: pytest.FixtureRequest) -> Mock:
    return mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)


@pytest.mark.parametrize(
    ("input_config", "reference_config"), zip(INPUT_CONFIGS, REFERENCE_CONFIGS, strict=True)
)
def test_parse(input_config: LoadedConfig, reference_config: LoadedConfig, platform: Mock) -> None:
    sync_tasks = parse(input_config)

    assert platform.assert_called_once
    assert isinstance(sync_tasks, list)
    assert len(sync_tasks) == len(input_config)

    ref_tasks = parse(reference_config)

    for sync_task, ref_task in zip(sync_tasks, ref_tasks, strict=True):
        print("Comparing tasks:")
        print(sync_task)
        print(ref_task)
        assert sync_task == ref_task
