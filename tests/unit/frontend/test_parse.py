from typing import TYPE_CHECKING

import pytest

from recnys.frontend.parse import parse
from recnys.frontend.task import Policy

if TYPE_CHECKING:
    from unittest.mock import Mock

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


class TestParse:
    def parse_test(
        self, input_config: LoadedConfig, reference_config: LoadedConfig, platform: Mock
    ) -> None:
        sync_tasks = parse(input_config)

        platform.assert_called()
        assert isinstance(sync_tasks, list)
        assert len(sync_tasks) == len(input_config)

        ref_tasks = parse(reference_config)

        for sync_task, ref_task in zip(sync_tasks, ref_tasks, strict=True):
            assert sync_task == ref_task

    @pytest.mark.parametrize(
        ("input_config", "reference_config"), zip(INPUT_CONFIGS, REFERENCE_CONFIGS, strict=True)
    )
    def test_individual(
        self, input_config: LoadedConfig, reference_config: LoadedConfig, platform: Mock
    ) -> None:
        self.parse_test(input_config, reference_config, platform)

    @pytest.mark.parametrize(
        ("input_configs", "reference_configs"), [(INPUT_CONFIGS, REFERENCE_CONFIGS)]
    )
    def test_merged(
        self,
        input_configs: list[LoadedConfig],
        reference_configs: list[LoadedConfig],
        platform: Mock,
    ) -> None:
        merged_input_config: LoadedConfig = {}
        for input_config in input_configs:
            merged_input_config.update(input_config)

        merged_reference_config: LoadedConfig = {}
        for reference_config in reference_configs:
            merged_reference_config.update(reference_config)

        self.parse_test(merged_input_config, merged_reference_config, platform)
