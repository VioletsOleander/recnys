"""Tests for backend syncer module."""

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

from recnys.backend.state import SyncDecision, SyncState, TaskSyncState
from recnys.backend.syncer import Syncer
from recnys.backend.utils import get_file_hash
from recnys.frontend.task import Policy

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from recnys.frontend.task import SyncTask


class TestSyncer:
    """Tests for Syncer class."""

    def test_sync_new_file_overwrite(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test syncing a new file with overwrite policy."""
        # Setup source file
        src_path = Path("/home/user/repo/.vimrc")
        fs.create_file(src_path, contents="set number\n")

        # Setup destination path
        dst_path = Path("/home/user/.vimrc")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)
        sync_state = SyncState()

        # Mock prompt to auto-confirm
        mocker.patch("recnys.backend.syncer.prompt_for_confirmation", return_value=True)

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination file was created with correct content
        assert dst_path.exists()
        assert dst_path.read_text() == "set number\n"

        # Verify state was updated
        assert src_path in result_state
        assert result_state[src_path].sync_decision == SyncDecision.NEW_FILE

    def test_sync_new_file_source_policy(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test syncing a new file with source policy."""
        # Setup source file
        src_path = Path("/home/user/repo/.bashrc")
        fs.create_file(src_path, contents="export PATH=/usr/local/bin:$PATH\n")

        # Setup destination path
        dst_path = Path("/home/user/.bashrc")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.SOURCE, False)
        sync_state = SyncState()

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination file was created with source statement
        assert dst_path.exists()
        content = dst_path.read_text()
        assert content.startswith(f'source "{src_path}"')

        # Verify state was updated
        assert src_path in result_state
        assert result_state[src_path].sync_decision == SyncDecision.NEW_FILE

    def test_sync_skip_unchanged_file(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test that unchanged files are skipped."""
        # Setup source and destination files with same content
        src_path = Path("/home/user/repo/.vimrc")
        dst_path = Path("/home/user/.vimrc")
        content = "set number\n"
        fs.create_file(src_path, contents=content)
        fs.create_file(dst_path, contents=content)

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)

        # Setup state with existing sync
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash=get_file_hash(src_path),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        syncer = Syncer(sync_state, [sync_task])

        # Verify skip was logged
        with patch("recnys.backend.syncer.logger") as mock_logger:
            syncer.sync(force=True)
            mock_logger.info.assert_any_call("Skipping sync for %s", src_path)

    def test_sync_modified_source(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test syncing when source file is modified."""
        # Setup source and destination files
        src_path = Path("/home/user/repo/.vimrc")
        dst_path = Path("/home/user/.vimrc")
        fs.create_file(src_path, contents="set number\n")
        fs.create_file(dst_path, contents="set number\n")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)

        # Setup state with old hash
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash="old_hash",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        # Modify source
        src_path.write_text("set number\nset relativenumber\n")

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination was updated
        assert dst_path.read_text() == "set number\nset relativenumber\n"

        # Verify state was updated with new decision
        assert result_state[src_path].sync_decision == SyncDecision.SRC_MODIFIED

    def test_sync_missing_destination(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test syncing when destination file is missing."""
        # Setup source file
        src_path = Path("/home/user/repo/.vimrc")
        dst_path = Path("/home/user/.vimrc")
        fs.create_file(src_path, contents="set number\n")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)

        # Setup state as if destination existed before
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash=get_file_hash(src_path),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination was created
        assert dst_path.exists()

        # Verify state has DST_MISSING decision
        assert result_state[src_path].sync_decision == SyncDecision.DST_MISSING

    def test_sync_modified_destination_overwrite(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
        """Test syncing when destination is modified (overwrite policy)."""
        # Setup source and destination files
        src_path = Path("/home/user/repo/.vimrc")
        dst_path = Path("/home/user/.vimrc")
        fs.create_file(src_path, contents="set number\n")
        fs.create_file(dst_path, contents="set number\n")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)

        # Setup state
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash=get_file_hash(src_path),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        # Modify destination
        dst_path.write_text("set number\nset modified by user\n")

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination was synced (overwritten)
        assert dst_path.read_text() == "set number\n"

        # Verify state has DST_MODIFIED decision
        assert result_state[src_path].sync_decision == SyncDecision.DST_MODIFIED

    def test_sync_source_policy_missing_source_statement(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
        """Test source policy when destination exists but lacks source statement."""
        # Setup source file
        src_path = Path("/home/user/repo/.bashrc")
        fs.create_file(src_path, contents="export MY_VAR=value\n")

        # Setup destination WITHOUT source statement
        dst_path = Path("/home/user/.bashrc")
        original_content = "# Existing bashrc\n"
        fs.create_file(dst_path, contents=original_content)

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.SOURCE, False)

        # Setup state
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash=get_file_hash(src_path),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify destination was updated with source statement
        content = dst_path.read_text()
        assert content.startswith(f'source "{src_path}"')

        # Verify DST_MODIFIED decision
        assert result_state[src_path].sync_decision == SyncDecision.DST_MODIFIED

    def test_sync_source_policy_with_source_statement(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
        """Test source policy when destination already has source statement."""
        # Setup source file
        src_path = Path("/home/user/repo/.bashrc")
        fs.create_file(src_path, contents="export MY_VAR=value\n")

        # Setup destination WITH source statement
        dst_path = Path("/home/user/.bashrc")
        content = f'source "{src_path}"\n\n# Existing bashrc\n'
        fs.create_file(dst_path, contents=content)

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.SOURCE, False)

        # Setup state
        sync_state = SyncState()
        sync_state[src_path] = TaskSyncState(
            dst=str(dst_path),
            file_hash=get_file_hash(src_path),
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )

        syncer = Syncer(sync_state, [sync_task])

        # Capture logs to verify skip message
        with patch("recnys.backend.syncer.logger") as mock_logger:
            syncer.sync(force=True)

            # Should be skipped since everything is up to date
            mock_logger.info.assert_any_call("Skipping sync for %s", src_path)

    def test_sync_user_declined(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test that sync respects user declining confirmation."""
        # Setup source file
        src_path = Path("/home/user/repo/.vimrc")
        dst_path = Path("/home/user/.vimrc")
        fs.create_file(src_path, contents="set number\n")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)
        sync_state = SyncState()

        # Mock prompt to decline
        mocker.patch("recnys.backend.syncer.prompt_for_confirmation", return_value=False)

        syncer = Syncer(sync_state, [sync_task])

        with patch("recnys.backend.syncer.logger") as mock_logger:
            syncer.sync(force=False)

            # Verify destination was NOT created
            assert not dst_path.exists()

            # Verify decline was logged (user declined message shows up in the temp file path)
            mock_logger.info.assert_any_call(
                "User declined to %s to %s",
                "overwrite",
                dst_path.with_suffix(dst_path.suffix + ".tmp_sync"),
            )

    def test_sync_directory(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test syncing a directory with multiple files."""
        # Setup source directory with files
        src_dir = Path("/home/user/repo/.config/nvim")
        fs.create_file(src_dir / "init.vim", contents="set number\n")
        fs.create_file(src_dir / "plugins.vim", contents="call plug#begin()\n")

        # Setup destination
        dst_dir = Path("/home/user/.config/nvim")

        # Create sync task for directory
        sync_task = self._create_sync_task(mocker, src_dir, dst_dir, Policy.OVERWRITE, True)
        sync_state = SyncState()

        syncer = Syncer(sync_state, [sync_task])
        result_state = syncer.sync(force=True)

        # Verify all files were synced
        assert (dst_dir / "init.vim").exists()
        assert (dst_dir / "plugins.vim").exists()
        assert (dst_dir / "init.vim").read_text() == "set number\n"
        assert (dst_dir / "plugins.vim").read_text() == "call plug#begin()\n"

        # Verify state was updated for each file
        assert src_dir / "init.vim" in result_state
        assert src_dir / "plugins.vim" in result_state

    def test_sync_with_exception_handling(self, fs: FakeFilesystem, mocker: MockerFixture) -> None:
        """Test that sync handles exceptions gracefully."""
        # Setup source file
        src_path = Path("/home/user/repo/.vimrc")
        fs.create_file(src_path, contents="set number\n")

        # Setup destination
        dst_path = Path("/home/user/.vimrc")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)
        sync_state = SyncState()

        # Make destination's parent read-only to cause an error
        mocker.patch(
            "recnys.backend.syncer.Syncer._sync_file", side_effect=Exception("Test exception")
        )

        syncer = Syncer(sync_state, [sync_task])

        with patch("recnys.backend.syncer.logger") as mock_logger:
            result_state = syncer.sync(force=True)

            # Verify exception was logged
            mock_logger.exception.assert_called()

            # Verify state wasn't updated on failure
            assert src_path not in result_state

    def test_sync_source_policy_prepends_to_existing(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
        """Test source policy prepends to existing file content."""
        # Setup source file
        src_path = Path("/home/user/repo/.bashrc")
        fs.create_file(src_path, contents="export MY_VAR=value\n")

        # Setup destination with existing content
        dst_path = Path("/home/user/.bashrc")
        original_content = "# Existing bashrc\nexport PATH=/usr/bin\n"
        fs.create_file(dst_path, contents=original_content)

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.SOURCE, False)
        sync_state = SyncState()

        syncer = Syncer(sync_state, [sync_task])
        syncer.sync(force=True)

        # Verify source statement was prepended
        content = dst_path.read_text()
        assert content.startswith(f'source "{src_path}"')

    def test_sync_creates_parent_directories(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
        """Test that sync creates parent directories if they don't exist."""
        # Setup source file
        src_path = Path("/home/user/repo/.config/nvim/init.vim")
        fs.create_file(src_path, contents="set number\n")

        # Setup destination in non-existent directory
        dst_path = Path("/home/user/.config/nvim/init.vim")

        # Create sync task
        sync_task = self._create_sync_task(mocker, src_path, dst_path, Policy.OVERWRITE, False)
        sync_state = SyncState()

        syncer = Syncer(sync_state, [sync_task])
        syncer.sync(force=True)

        # Verify parent directories were created
        assert dst_path.parent.exists()
        assert dst_path.exists()
        assert dst_path.read_text() == "set number\n"

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
