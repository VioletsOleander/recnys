"""Tests for backend syncer module."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import Mock, patch

import pytest

from recnys.backend.state import SyncDecision, SyncState
from recnys.backend.syncer import Syncer
from recnys.frontend.task import Policy

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem
    from pytest_mock import MockerFixture

    from recnys.frontend.task import SyncTask


class TestSyncer:
    """Tests for Syncer class."""

    def test_sync_new_file_overwrite(
        self, fs: FakeFilesystem, mocker: MockerFixture
    ) -> None:
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
