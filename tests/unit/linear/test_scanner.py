import pytest
from pydantic_core import ValidationError

from recnys.linear.scanner import scan_config
from recnys.testing.unit.linear.constants import INVALID_CONFIGS


@pytest.mark.parametrize("loaded_config", INVALID_CONFIGS)
def test_scan_config(loaded_config: dict) -> None:
    with pytest.raises(ValidationError):
        scan_config(loaded_config=loaded_config)
