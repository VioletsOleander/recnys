from typing import TYPE_CHECKING

import pytest
from pydantic_core import ValidationError

from recnys.linear.validator import validate_config
from recnys.testing.unit.linear.constants import INVALID_CONFIGS, SOURCES

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.linear.model import ScannedConfig


@pytest.mark.parametrize("invalid_config", INVALID_CONFIGS)
def test_validate_config(filesystem: FakeFilesystem, invalid_config: ScannedConfig) -> None:
    for s in SOURCES:
        filesystem.create_file(s.path, contents=s.content)

    with pytest.raises(ValidationError):
        validate_config(scanned_config=invalid_config)
