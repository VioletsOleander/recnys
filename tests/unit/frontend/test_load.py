from pathlib import Path
from typing import TYPE_CHECKING

from recnys.frontend.load import load
from recnys.testing.frontend.arranger import init_filesystem

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.frontend.load import LoadedConfig


def test_load(filesystem: FakeFilesystem, loaded_config: LoadedConfig) -> None:
    file_path = Path.home() / Path("recnys.yaml")
    init_filesystem(filesystem=filesystem, file_path=file_path)

    result = load(file_path=file_path)

    assert result == loaded_config
