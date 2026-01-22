from typing import TYPE_CHECKING

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem, OSType

if TYPE_CHECKING:
    from pytest_mock import MockerFixture


@pytest.fixture(params=["Linux", "Windows"])
def system(mocker: MockerFixture, request: pytest.FixtureRequest) -> str:
    mock = mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)
    return mock.return_value


@pytest.fixture
def filesystem(fs: FakeFilesystem, system: str) -> FakeFilesystem:
    fs.os = OSType(system.lower())
    return fs
