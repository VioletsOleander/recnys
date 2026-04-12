import platform
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem, OSType


@pytest.fixture
def resources_dir(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath / "tests" / "resources"


@pytest.fixture(params=["Linux", "Windows"])
def system(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> str:
    monkeypatch.setattr(platform, "system", lambda: request.param)
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
