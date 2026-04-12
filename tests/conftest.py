from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem, OSType

if TYPE_CHECKING:
    from pytest_mock import MockFixture


@pytest.fixture
def resources_dir(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath / "tests" / "resources"


@pytest.fixture(params=["Linux", "Windows"])
def system(mocker: MockFixture, request: pytest.FixtureRequest) -> str:
    mocker.patch("recnys.tree.ctree.builder.platform.system", return_value=request.param)
    return request.param


@pytest.fixture
def filesystem(fs: FakeFilesystem, monkeypatch: pytest.MonkeyPatch, system: str) -> FakeFilesystem:
    fs.os = OSType(system.lower())

    match system:
        case "Linux":
            monkeypatch.setattr(Path, "home", lambda: Path("/home/bob"))
            fs.create_dir("/home/bob")
        case "Windows":
            monkeypatch.setattr(Path, "home", lambda: Path("C:/Users/bob"))
            fs.create_dir("C:/Users/bob")

    return fs
