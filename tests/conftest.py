import os
import platform
from pathlib import Path

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem, OSType


@pytest.fixture(params=["Linux", "Windows"])
def system(monkeypatch: pytest.MonkeyPatch, request: pytest.FixtureRequest) -> str:
    monkeypatch.setattr(platform, "system", lambda: request.param)
    return request.param


@pytest.fixture
def filesystem(fs: FakeFilesystem, system: str, monkeypatch: pytest.MonkeyPatch) -> FakeFilesystem:
    fs.os = OSType(system.lower())

    match system:
        case "Linux":
            home = Path("/home/test-user")
        case "Windows":
            home = Path("C:/Users/test-user")

    fs.create_dir(home)
    monkeypatch.setattr(Path, "home", lambda: home)

    cwd = home / "test-repo"
    fs.create_dir(cwd)
    os.chdir(cwd)

    return fs
