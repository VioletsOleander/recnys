"""Tests for backend syncer module."""

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from recnys.backend.state import SyncDecision, SyncState, TaskSyncState
from recnys.backend.syncer import Syncer
from recnys.backend.utils import get_file_hash
from recnys.frontend.task import Policy

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from recnys.frontend.task import SyncTask


@pytest.fixture
def src_dst_paths() -> tuple[Path, Path]:
    """Fixture providing common source and destination paths."""
    return Path("/home/user/repo/.vimrc"), Path("/home/user/.vimrc")


@pytest.fixture
def bashrc_paths() -> tuple[Path, Path]:
    """Fixture providing bashrc paths."""
    return Path("/home/user/repo/.bashrc"), Path("/home/user/.bashrc")


@pytest.fixture
def nvim_paths() -> tuple[Path, Path]:
    """Fixture providing nvim config paths."""
    return Path("/home/user/repo/.config/nvim"), Path("/home/user/.config/nvim")


class TestSyncer:
    """Tests for Syncer class."""

    def _setup_files(
        self,
        fs: FakeFilesystem,
        src: Path,
        dst: Path | None,
        src_content: str,
        dst_content: str | None = None,
    ) -> None:
        """Helper to set up source and optionally destination files."""
        fs.create_file(src, contents=src_content)
        if dst is not None and dst_content is not None:
            fs.create_file(dst, contents=dst_content)

    def _create_task_state(
        self, src: Path, dst: Path, hash_value: str | None = None
    ) -> TaskSyncState:
        """Helper to create a TaskSyncState."""
        return TaskSyncState(
            dst=str(dst),
            file_hash=hash_value or get_file_hash(src),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

    def _run_sync(  # noqa: PLR0913
        self,
        mocker: MockerFixture,
        fs: FakeFilesystem,
        src: Path,
        dst: Path,
        policy: Policy,
        *,
        sync_state: SyncState | None = None,
        force: bool = True,
    ) -> tuple[Syncer, SyncState]:
        """Helper to create syncer and run sync."""
        sync_task = self._create_sync_task(mocker, src, dst, policy, False)
        state = sync_state or SyncState()
        syncer = Syncer(state, [sync_task])
        result_state = syncer.sync(force=force)
        return syncer, result_state

    def test_sync_new_file_overwrite(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing a new file with overwrite policy."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, None, "set number\n")

        _, result_state = self._run_sync(mocker, fs, src_path, dst_path, Policy.OVERWRITE)

        assert dst_path.exists()
        assert dst_path.read_text() == "set number\n"
        assert src_path in result_state
        assert result_state[src_path].sync_decision == SyncDecision.NEW_FILE

    def test_sync_new_file_source_policy(
        self, fs: FakeFilesystem, mocker: MockerFixture, bashrc_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing a new file with source policy."""
        src_path, dst_path = bashrc_paths
        self._setup_files(fs, src_path, None, "export PATH=/usr/local/bin:$PATH\n")

        _, result_state = self._run_sync(mocker, fs, src_path, dst_path, Policy.SOURCE)

        assert dst_path.exists()
        assert dst_path.read_text().startswith(f'source "{src_path}"')
        assert src_path in result_state
        assert result_state[src_path].sync_decision == SyncDecision.NEW_FILE

    def test_sync_skip_unchanged_file(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test that unchanged files are skipped."""
        src_path, dst_path = src_dst_paths
        content = "set number\n"
        self._setup_files(fs, src_path, dst_path, content, content)

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path)

        with patch("recnys.backend.syncer.logger") as mock_logger:
            self._run_sync(mocker, fs, src_path, dst_path, Policy.OVERWRITE, sync_state=sync_state)
            mock_logger.info.assert_any_call("Skipping sync for %s", src_path)

    def test_sync_modified_source(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing when source file is modified."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, dst_path, "set number\n", "set number\n")

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path, "old_hash")

        # Modify source
        src_path.write_text("set number\nset relativenumber\n")

        _, result_state = self._run_sync(
            mocker, fs, src_path, dst_path, Policy.OVERWRITE, sync_state=sync_state
        )

        assert dst_path.read_text() == "set number\nset relativenumber\n"
        assert result_state[src_path].sync_decision == SyncDecision.SRC_MODIFIED

    def test_sync_missing_destination(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing when destination file is missing."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, None, "set number\n")

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path)

        _, result_state = self._run_sync(
            mocker, fs, src_path, dst_path, Policy.OVERWRITE, sync_state=sync_state
        )

        assert dst_path.exists()
        assert result_state[src_path].sync_decision == SyncDecision.DST_MISSING

    def test_sync_modified_destination_overwrite(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing when destination is modified (overwrite policy)."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, dst_path, "set number\n", "set number\n")

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path)

        # Modify destination
        dst_path.write_text("set number\nset modified by user\n")

        _, result_state = self._run_sync(
            mocker, fs, src_path, dst_path, Policy.OVERWRITE, sync_state=sync_state
        )

        assert dst_path.read_text() == "set number\n"
        assert result_state[src_path].sync_decision == SyncDecision.DST_MODIFIED

    def test_sync_source_policy_missing_source_statement(
        self, fs: FakeFilesystem, mocker: MockerFixture, bashrc_paths: tuple[Path, Path]
    ) -> None:
        """Test source policy when destination exists but lacks source statement."""
        src_path, dst_path = bashrc_paths
        self._setup_files(fs, src_path, dst_path, "export MY_VAR=value\n", "# Existing bashrc\n")

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path)

        _, result_state = self._run_sync(
            mocker, fs, src_path, dst_path, Policy.SOURCE, sync_state=sync_state
        )

        assert dst_path.read_text().startswith(f'source "{src_path}"')
        assert result_state[src_path].sync_decision == SyncDecision.DST_MODIFIED

    def test_sync_source_policy_with_source_statement(
        self, fs: FakeFilesystem, mocker: MockerFixture, bashrc_paths: tuple[Path, Path]
    ) -> None:
        """Test source policy when destination already has source statement."""
        src_path, dst_path = bashrc_paths
        self._setup_files(
            fs,
            src_path,
            dst_path,
            "export MY_VAR=value\n",
            f'source "{src_path}"\n\n# Existing bashrc\n',
        )

        sync_state = SyncState()
        sync_state[src_path] = self._create_task_state(src_path, dst_path)

        with patch("recnys.backend.syncer.logger") as mock_logger:
            self._run_sync(mocker, fs, src_path, dst_path, Policy.SOURCE, sync_state=sync_state)
            mock_logger.info.assert_any_call("Skipping sync for %s", src_path)

    def test_sync_user_declined(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test that sync respects user declining confirmation."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, None, "set number\n")

        mocker.patch("recnys.backend.syncer.prompt_for_confirmation", return_value=False)

        with patch("recnys.backend.syncer.logger") as mock_logger:
            self._run_sync(mocker, fs, src_path, dst_path, Policy.OVERWRITE, force=False)

            assert not dst_path.exists()
            mock_logger.info.assert_any_call(
                "User declined to %s to %s",
                "overwrite",
                dst_path.with_suffix(dst_path.suffix + ".tmp_sync"),
            )

    def test_sync_directory(
        self, fs: FakeFilesystem, mocker: MockerFixture, nvim_paths: tuple[Path, Path]
    ) -> None:
        """Test syncing a directory with multiple files."""
        src_dir, dst_dir = nvim_paths
        fs.create_file(src_dir / "init.vim", contents="set number\n")
        fs.create_file(src_dir / "plugins.vim", contents="call plug#begin()\n")

        sync_task = self._create_sync_task(mocker, src_dir, dst_dir, Policy.OVERWRITE, True)
        syncer = Syncer(SyncState(), [sync_task])
        result_state = syncer.sync(force=True)

        assert (dst_dir / "init.vim").exists()
        assert (dst_dir / "plugins.vim").exists()
        assert (dst_dir / "init.vim").read_text() == "set number\n"
        assert (dst_dir / "plugins.vim").read_text() == "call plug#begin()\n"
        assert src_dir / "init.vim" in result_state
        assert src_dir / "plugins.vim" in result_state

    def test_sync_with_exception_handling(
        self, fs: FakeFilesystem, mocker: MockerFixture, src_dst_paths: tuple[Path, Path]
    ) -> None:
        """Test that sync handles exceptions gracefully."""
        src_path, dst_path = src_dst_paths
        self._setup_files(fs, src_path, None, "set number\n")

        mocker.patch(
            "recnys.backend.syncer.Syncer._sync_file", side_effect=Exception("Test exception")
        )

        with patch("recnys.backend.syncer.logger") as mock_logger:
            _, result_state = self._run_sync(mocker, fs, src_path, dst_path, Policy.OVERWRITE)

            mock_logger.exception.assert_called()
            assert src_path not in result_state

    def test_sync_source_policy_prepends_to_existing(
        self, fs: FakeFilesystem, mocker: MockerFixture, bashrc_paths: tuple[Path, Path]
    ) -> None:
        """Test source policy prepends to existing file content."""
        src_path, dst_path = bashrc_paths
        self._setup_files(
            fs,
            src_path,
            dst_path,
            "export MY_VAR=value\n",
            "# Existing bashrc\nexport PATH=/usr/bin\n",
        )

        _, _ = self._run_sync(mocker, fs, src_path, dst_path, Policy.SOURCE)

        assert dst_path.read_text().startswith(f'source "{src_path}"')

    def test_sync_creates_parent_directories(
        self, fs: FakeFilesystem, mocker: MockerFixture, nvim_paths: tuple[Path, Path]
    ) -> None:
        """Test that sync creates parent directories if they don't exist."""
        src_dir, dst_dir = nvim_paths
        src_file = src_dir / "init.vim"
        dst_file = dst_dir / "init.vim"
        self._setup_files(fs, src_file, None, "set number\n")

        _, _ = self._run_sync(mocker, fs, src_file, dst_file, Policy.OVERWRITE)

        assert dst_file.parent.exists()
        assert dst_file.exists()
        assert dst_file.read_text() == "set number\n"

    def _create_sync_task(
        self,
        mocker: MockerFixture,
        src_path: Path,
        dst_path: Path,
        policy: Policy,
        is_dir: bool,
    ) -> SyncTask:
        """Helper to create a mock SyncTask."""
        from recnys.frontend.task import SyncTask

        # Create mock Src
        mock_src = Mock()
        mock_src.path = src_path
        mock_src.is_dir = is_dir

        # Create mock Dst
        mock_dst = Mock()
        mock_dst.path = dst_path

        # Create SyncTask
        sync_task = Mock(spec=SyncTask)
        sync_task.src = mock_src
        sync_task.dst = mock_dst
        sync_task.policy = policy

        return sync_task
