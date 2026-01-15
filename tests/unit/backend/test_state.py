"""Tests for backend state management."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.backend.state import SyncDecision, SyncState, TaskSyncState

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


class TestTaskSyncState:
    """Tests for TaskSyncState dataclass."""

    def test_create_task_sync_state(self) -> None:
        """Test creating a TaskSyncState."""
        state = TaskSyncState(
            dst="/home/user/.vimrc",
            file_hash="abc123",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )
        
        assert state.dst == "/home/user/.vimrc"
        assert state.file_hash == "abc123"
        assert state.last_sync_time == "2024-01-15T10:00:00"
        assert state.sync_decision == SyncDecision.NEW_FILE

    def test_from_dict(self) -> None:
        """Test creating TaskSyncState from dictionary."""
        data = {
            "dst": "/home/user/.bashrc",
            "file_hash": "def456",
            "last_sync_time": "2024-01-15T11:00:00",
            "sync_decision": "New file to be synchronized",
        }
        
        state = TaskSyncState.from_dict(data)
        
        assert state.dst == "/home/user/.bashrc"
        assert state.file_hash == "def456"
        assert state.last_sync_time == "2024-01-15T11:00:00"
        assert state.sync_decision == SyncDecision.NEW_FILE

    def test_immutability(self) -> None:
        """Test that TaskSyncState is frozen (immutable)."""
        state = TaskSyncState(
            dst="/home/user/.vimrc",
            file_hash="abc123",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )
        
        with pytest.raises(Exception):  # FrozenInstanceError
            state.dst = "/home/user/other"  # type: ignore[misc]


class TestSyncState:
    """Tests for SyncState class."""

    def test_create_empty_sync_state(self) -> None:
        """Test creating an empty SyncState."""
        state = SyncState()
        
        assert len(state) == 0

    def test_set_and_get_item(self, fs: FakeFilesystem) -> None:
        """Test setting and getting items in SyncState."""
        state = SyncState()
        src_path = Path("/tmp/test.txt")
        
        task_state = TaskSyncState(
            dst="/home/user/test.txt",
            file_hash="abc123",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )
        
        state[src_path] = task_state
        
        assert state[src_path] == task_state
        assert len(state) == 1

    def test_delete_item(self, fs: FakeFilesystem) -> None:
        """Test deleting items from SyncState."""
        state = SyncState()
        src_path = Path("/tmp/test.txt")
        
        task_state = TaskSyncState(
            dst="/home/user/test.txt",
            file_hash="abc123",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )
        
        state[src_path] = task_state
        del state[src_path]
        
        assert len(state) == 0

    def test_iteration(self, fs: FakeFilesystem) -> None:
        """Test iterating over SyncState."""
        state = SyncState()
        paths = [Path("/tmp/file1.txt"), Path("/tmp/file2.txt")]
        
        for path in paths:
            state[path] = TaskSyncState(
                dst=f"/home/user/{path.name}",
                file_hash="hash",
                last_sync_time="2024-01-15T10:00:00",
                sync_decision=SyncDecision.NEW_FILE,
            )
        
        assert len(state) == 2
        assert set(state) == set(paths)

    def test_get_nonexistent_key(self, fs: FakeFilesystem) -> None:
        """Test accessing a non-existent key raises KeyError."""
        state = SyncState()
        
        with pytest.raises(KeyError):
            _ = state[Path("/tmp/nonexistent.txt")]

    def test_get_method(self, fs: FakeFilesystem) -> None:
        """Test the get method returns None for non-existent keys."""
        state = SyncState()
        
        result = state.get(Path("/tmp/nonexistent.txt"))
        
        assert result is None

    def test_save_and_load_empty_state(self, fs: FakeFilesystem) -> None:
        """Test saving and loading an empty SyncState."""
        state_file = Path("/tmp/sync_state.json")
        state = SyncState()
        
        state.save(state_file)
        
        loaded_state = SyncState.from_json(state_file)
        
        assert len(loaded_state) == 0

    def test_save_and_load_state_with_data(self, fs: FakeFilesystem) -> None:
        """Test saving and loading a SyncState with data."""
        state_file = Path("/tmp/sync_state.json")
        state = SyncState()
        
        src_path = Path("/tmp/test.txt")
        task_state = TaskSyncState(
            dst="/home/user/test.txt",
            file_hash="abc123",
            last_sync_time="2024-01-15T10:00:00",
            sync_decision=SyncDecision.NEW_FILE,
        )
        state[src_path] = task_state
        
        state.save(state_file)
        loaded_state = SyncState.from_json(state_file)
        
        assert len(loaded_state) == 1
        loaded_task_state = loaded_state[src_path]
        assert loaded_task_state.dst == task_state.dst
        assert loaded_task_state.file_hash == task_state.file_hash
        assert loaded_task_state.last_sync_time == task_state.last_sync_time
        assert loaded_task_state.sync_decision == task_state.sync_decision

    def test_load_nonexistent_file(self, fs: FakeFilesystem) -> None:
        """Test loading from a non-existent file creates empty state."""
        state_file = Path("/tmp/nonexistent_state.json")
        
        loaded_state = SyncState.from_json(state_file)
        
        assert len(loaded_state) == 0

    def test_save_multiple_entries(self, fs: FakeFilesystem) -> None:
        """Test saving and loading multiple entries."""
        state_file = Path("/tmp/sync_state.json")
        state = SyncState()
        
        paths = [Path("/tmp/file1.txt"), Path("/tmp/file2.txt"), Path("/tmp/file3.txt")]
        for i, path in enumerate(paths):
            state[path] = TaskSyncState(
                dst=f"/home/user/file{i}.txt",
                file_hash=f"hash{i}",
                last_sync_time=f"2024-01-15T10:0{i}:00",
                sync_decision=SyncDecision.NEW_FILE,
            )
        
        state.save(state_file)
        loaded_state = SyncState.from_json(state_file)
        
        assert len(loaded_state) == 3
        for i, path in enumerate(paths):
            task_state = loaded_state[path]
            assert task_state.dst == f"/home/user/file{i}.txt"
            assert task_state.file_hash == f"hash{i}"


class TestSyncDecision:
    """Tests for SyncDecision enum."""

    def test_sync_decision_values(self) -> None:
        """Test that SyncDecision enum has expected values."""
        assert SyncDecision.SKIP.value == "Update to date, skip synchronization"
        assert SyncDecision.NEW_FILE.value == "New file to be synchronized"
        assert SyncDecision.SRC_MODIFIED.value == "Source File is modified (hash mismatch) since last sync"
        assert SyncDecision.DST_MISSING.value == "Destination file does not exist or is deleted since last sync"
        assert SyncDecision.DST_MODIFIED.value == "Destination file is modified (hash mismatch) since last sync"
