"""Tests for syncer module, particularly line ending preservation."""

import tempfile
from pathlib import Path

import pytest

from recnys.backend.state import SyncState
from recnys.backend.syncer import Syncer, _make_sync_decision
from recnys.backend.task import CanonicalSyncTask
from recnys.backend.utils import get_file_hash
from recnys.frontend.task import Policy, SyncTask
from recnys.testing.frontend.utils import make_sync_task


def test_overwrite_preserves_line_endings_crlf(tmp_path: Path) -> None:
    """Test that OVERWRITE policy preserves CRLF line endings exactly."""
    # Create source file with CRLF line endings
    src_file = tmp_path / "source.txt"
    content_with_crlf = "line1\r\nline2\r\nline3\r\n"
    src_file.write_bytes(content_with_crlf.encode("utf-8"))
    
    # Create destination path
    dst_file = tmp_path / "dest.txt"
    
    # Create sync task with OVERWRITE policy
    sync_task = make_sync_task(
        src_path=src_file,
        src_is_dir=False,
        dst_path=dst_file,
        policy=Policy.OVERWRITE
    )
    
    # Perform sync
    sync_state = SyncState()
    syncer = Syncer(sync_state, [sync_task])
    syncer.sync(force=True)
    
    # Verify destination has exact same content (including CRLF)
    assert dst_file.read_bytes() == src_file.read_bytes()
    assert dst_file.read_bytes() == content_with_crlf.encode("utf-8")


def test_overwrite_preserves_line_endings_lf(tmp_path: Path) -> None:
    """Test that OVERWRITE policy preserves LF line endings exactly."""
    # Create source file with LF line endings
    src_file = tmp_path / "source.txt"
    content_with_lf = "line1\nline2\nline3\n"
    src_file.write_bytes(content_with_lf.encode("utf-8"))
    
    # Create destination path
    dst_file = tmp_path / "dest.txt"
    
    # Create sync task with OVERWRITE policy
    sync_task = make_sync_task(
        src_path=src_file,
        src_is_dir=False,
        dst_path=dst_file,
        policy=Policy.OVERWRITE
    )
    
    # Perform sync
    sync_state = SyncState()
    syncer = Syncer(sync_state, [sync_task])
    syncer.sync(force=True)
    
    # Verify destination has exact same content (including LF)
    assert dst_file.read_bytes() == src_file.read_bytes()
    assert dst_file.read_bytes() == content_with_lf.encode("utf-8")


def test_repeated_sync_with_crlf_does_not_retrigger(tmp_path: Path) -> None:
    """Test that a file with CRLF endings doesn't get repeatedly synced.
    
    This is the main bug fix: previously, text mode I/O could change line
    endings, causing hash mismatches and repeated syncs.
    """
    # Create source file with CRLF line endings
    src_file = tmp_path / "gitconfig"
    content_with_crlf = "[user]\r\n\tname = Test User\r\n\temail = test@example.com\r\n"
    src_file.write_bytes(content_with_crlf.encode("utf-8"))
    
    # Create destination path
    dst_file = tmp_path / "dest_gitconfig"
    
    # Create sync task
    sync_task = make_sync_task(
        src_path=src_file,
        src_is_dir=False,
        dst_path=dst_file,
        policy=Policy.OVERWRITE
    )
    
    # First sync
    sync_state = SyncState()
    syncer = Syncer(sync_state, [sync_task])
    updated_state = syncer.sync(force=True)
    
    # Verify file was synced
    assert dst_file.exists()
    assert dst_file.read_bytes() == src_file.read_bytes()
    
    # Get the source hash after sync
    src_hash_after_first = get_file_hash(src_file)
    dst_hash_after_first = get_file_hash(dst_file)
    assert src_hash_after_first == dst_hash_after_first
    
    # Second sync with same state - should skip
    syncer2 = Syncer(updated_state, [sync_task])
    
    # Check sync decision
    from recnys.backend.task import canonicalize_sync_tasks
    canonical_tasks = canonicalize_sync_tasks([sync_task])
    decision = _make_sync_decision(canonical_tasks[0], updated_state)
    
    # Should skip because nothing changed
    from recnys.backend.state import SyncDecision
    assert decision == SyncDecision.SKIP, f"Expected SKIP but got {decision}"
    
    # Verify hashes still match
    assert get_file_hash(src_file) == get_file_hash(dst_file)


def test_repeated_sync_with_mixed_line_endings(tmp_path: Path) -> None:
    """Test that files with mixed line endings are handled consistently."""
    # Create source file with mixed line endings (some CRLF, some LF)
    src_file = tmp_path / "mixed.txt"
    content_mixed = "line1\r\nline2\nline3\r\n"
    src_file.write_bytes(content_mixed.encode("utf-8"))
    
    # Create destination path
    dst_file = tmp_path / "dest_mixed.txt"
    
    # Create sync task
    sync_task = make_sync_task(
        src_path=src_file,
        src_is_dir=False,
        dst_path=dst_file,
        policy=Policy.OVERWRITE
    )
    
    # First sync
    sync_state = SyncState()
    syncer = Syncer(sync_state, [sync_task])
    updated_state = syncer.sync(force=True)
    
    # Verify exact copy
    assert dst_file.read_bytes() == src_file.read_bytes()
    
    # Second sync should skip
    from recnys.backend.task import canonicalize_sync_tasks
    from recnys.backend.state import SyncDecision
    
    canonical_tasks = canonicalize_sync_tasks([sync_task])
    decision = _make_sync_decision(canonical_tasks[0], updated_state)
    assert decision == SyncDecision.SKIP
