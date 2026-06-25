from argparse import Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.main import main
from recnys.testing.integration.arranger import create_config_files
from recnys.testing.integration.constants import LINUX_TARGETS, SOURCES, WINDOWS_TARGETS
from recnys.testing.node import File, Symlink

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.fixture
def recnys_file(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath / "tests" / "integration" / "resources" / "recnys.yaml"


@pytest.fixture
def variables_file(pytestconfig: pytest.Config) -> Path:
    return pytestconfig.rootpath / "tests" / "integration" / "resources" / "variables.yaml"


def test_integration(
    filesystem: FakeFilesystem, system: str, recnys_file: Path, variables_file: Path
) -> None:
    args = Namespace(silent=True, debug=False, dry_run=False)

    create_config_files(filesystem, recnys_file=recnys_file, variables_file=variables_file)
    for s in SOURCES:
        filesystem.create_file(s.path, contents=s.content)

    # Undecorate the main function
    main.__wrapped__(args)  # type: ignore[ty:unresolved-attribute]

    match system:
        case "Linux":
            targets = LINUX_TARGETS
        case "Windows":
            targets = WINDOWS_TARGETS

    for t in targets:
        if isinstance(t, File):
            content = (Path.home() / t.path).read_text()
            assert content == t.content
        elif isinstance(t, Symlink):
            assert (Path.home() / t.dst).readlink() == Path(t.src).resolve()
