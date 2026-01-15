from typing import TYPE_CHECKING

import pytest

from recnys.backend.task import CanonicalSyncTask
from recnys.testing.frontend.utils import make_sync_task

if TYPE_CHECKING:
    from unittest.mock import Mock

    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from recnys.frontend.task import SyncTask


@pytest.fixture(params=["Linux", "Windows"])
def platform(mocker: MockerFixture, request: pytest.FixtureRequest) -> Mock:
    return mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)


@pytest.fixture
def sync_tasks(fs: FakeFilesystem, platform: Mock) -> list[SyncTask]:
    """Create sync tasks with fake filesystem to ensure consistent paths."""
    from pathlib import Path

    from recnys.testing.frontend.constants import DST_PARAMS, POLICIES

    # Set up fake filesystem with proper cwd
    real_cwd = "/home/runner/work/recnys/recnys"
    if not fs.exists(real_cwd):
        fs.create_dir(real_cwd)
    fs.cwd = real_cwd

    # Define source params that match the pattern
    src_params_raw = (
        (Path(".vimrc"), False),
        (Path(".bashrc"), False),
        (Path(".inputrc"), False),
        (Path(".tmux.conf"), False),
        (Path(".gitconfig"), False),
        (Path(".config/nvim/"), True),
        (Path(".config/helix/"), True),
        (Path(".config/yazi/"), True),
    )
    src_params = tuple((Path(real_cwd) / p, is_dir) for p, is_dir in src_params_raw)

    return [
        make_sync_task(src_path=src_path, src_is_dir=src_is_dir, dst_path=dst_path, policy=policy)
        for (src_path, src_is_dir), dst_path, policy in zip(
            src_params, DST_PARAMS[platform.return_value], POLICIES, strict=True
        )
    ]


@pytest.fixture
def canonical_sync_tasks(
    fs: FakeFilesystem, platform: Mock
) -> list[CanonicalSyncTask]:
    """Create canonical sync tasks with fake filesystem to avoid polluting real filesystem."""
    from pathlib import Path

    from recnys.testing.backend.constants import DST_PATHS, POLICIES

    curr_os = platform.return_value

    # Set up fake filesystem with proper cwd
    real_cwd = "/home/runner/work/recnys/recnys"
    if not fs.exists(real_cwd):
        fs.create_dir(real_cwd)
    fs.cwd = real_cwd

    # Define source paths relative to fake cwd
    src_paths_linux = (
        Path(".vimrc"),
        Path(".bashrc"),
        Path(".inputrc"),
        Path(".tmux.conf"),
        Path(".gitconfig"),
        Path(".config/nvim/foo"),
        Path(".config/helix/foo"),
        Path(".config/yazi/foo"),
    )
    src_paths_linux = tuple(Path(real_cwd) / p for p in src_paths_linux)

    src_paths_windows = (
        Path(".vimrc"),
        None,
        None,
        None,
        Path(".gitconfig"),
        Path(".config/nvim/foo"),
        Path(".config/helix/foo"),
        Path(".config/yazi/foo"),
    )
    src_paths_windows = tuple(Path(real_cwd) / p for p in src_paths_windows if p is not None)

    src_paths = {"Linux": src_paths_linux, "Windows": src_paths_windows}

    # Create source files in fake filesystem
    for src_path in src_paths[curr_os]:
        fs.create_file(src_path)

    return [
        CanonicalSyncTask(src=src_path, dst=dst_path, policy=policy)
        for src_path, dst_path, policy in zip(
            src_paths[curr_os], DST_PATHS[curr_os], POLICIES[curr_os], strict=True
        )
    ]
    # No cleanup needed - pyfakefs automatically cleans up after the test
