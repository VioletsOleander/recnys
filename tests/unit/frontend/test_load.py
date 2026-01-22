from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.frontend.load import load
from recnys.testing.frontend.constants import CONFIG_FILE_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.frontend.load import LoadedConfig


@pytest.fixture
def config_file(filesystem: FakeFilesystem) -> Path:
    path = Path.home() / "recnys.yaml"
    filesystem.create_file(path, contents=CONFIG_FILE_CONTENT)
    return path


def test_load(config_file: Path, loaded_config: LoadedConfig) -> None:
    result = load(config_file)
    assert result == loaded_config
