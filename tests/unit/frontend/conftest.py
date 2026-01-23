from typing import TYPE_CHECKING

import pytest

from recnys.testing.frontend.constants import LOADED_CONFIG

if TYPE_CHECKING:
    from recnys.frontend.load import LoadedConfig


@pytest.fixture
def loaded_config() -> LoadedConfig:
    return LOADED_CONFIG
