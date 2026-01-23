from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncState
from recnys.backend.syncer import Syncer
from recnys.frontend.load import load
from recnys.frontend.parse import parse
from recnys.frontend.task import Policy
from recnys.testing.integration.constants import CONFIG_FILE_CONTENT
from recnys.testing.integration.utils import make_dest_files, make_policies, make_source_files

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.fixture
def config_file() -> Path:
    return Path("recnys.yaml")


@pytest.fixture
def state_file() -> Path:
    return Path(".sync_states.json")


@pytest.fixture
def source_files(system: str) -> list[Path]:
    return make_source_files(system)


@pytest.fixture
def dest_files(system: str) -> list[Path]:
    return make_dest_files(system)


@pytest.fixture
def policies(system: str) -> list[Policy]:
    return make_policies(system)


@pytest.fixture
def filesystem(
    filesystem: FakeFilesystem, config_file: Path, source_files: list[Path]
) -> FakeFilesystem:
    filesystem.create_file(config_file, contents=CONFIG_FILE_CONTENT)
    for f in source_files:
        filesystem.create_file(file_path=f, contents="dummy content")
    return filesystem


@pytest.mark.usefixtures("filesystem")
def test_integration(
    config_file: Path,
    state_file: Path,
    source_files: list[Path],
    dest_files: list[Path],
    policies: list[Policy],
) -> None:
    config = load(config_file)
    tasks = parse(config)
    state = SyncState.from_json(state_file)
    syncer = Syncer(sync_state=state, sync_tasks=tasks)
    syncer.sync(force=True)

    for src, dst, policy in zip(source_files, dest_files, policies, strict=True):
        assert dst.exists()
        with src.open("r") as src_file, dst.open("r") as dst_file:
            if policy == Policy.OVERWRITE:
                assert src_file.read() == dst_file.read()
            elif policy == Policy.SOURCE:
                assert dst_file.read().strip() == f'source "{src}"'
