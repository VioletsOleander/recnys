from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.load import load_config, load_variables
from recnys.testing.load.arrange import create_config_file, create_variables_file
from recnys.testing.load.constants import LOADED_CONFIG, LOADED_VARIABLES


def test_load_config(filesystem: FakeFilesystem) -> None:
    path = create_config_file(filesystem=filesystem)

    result = load_config(file_path=path)

    assert result == LOADED_CONFIG


def test_load_variables(filesystem: FakeFilesystem) -> None:
    path = create_variables_file(filesystem=filesystem)

    result = load_variables(file_path=path)

    assert result == LOADED_VARIABLES
