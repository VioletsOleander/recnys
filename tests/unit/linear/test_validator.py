from typing import TYPE_CHECKING

import pytest
from pydantic_core import ValidationError

from recnys.linear.validator import validate_config
from recnys.testing.arranger import create_source_files, setup_cwd
from recnys.testing.unit.linear.constants import INVALID_CONFIGS, SOURCE_FILES

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.linear.model import ScannedConfig


@pytest.mark.parametrize("invalid_config", INVALID_CONFIGS)
def test_validate_config(filesystem: FakeFilesystem, invalid_config: ScannedConfig) -> None:
    setup_cwd(filesystem)
    create_source_files(filesystem, source_files=SOURCE_FILES)

    with pytest.raises(ValidationError):
        validate_config(scanned_config=invalid_config)
