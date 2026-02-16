"""Tests for symlink synchronization policy."""

from pathlib import Path
from typing import TYPE_CHECKING

from recnys.io.record import ExecutionRecord
from recnys.sync.syncer import FileSyncer
from recnys.sync.task import FileSyncPolicy, FileSyncTask
from recnys.testing.sync.constants import NORMAL_FILE_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_symlink_policy(filesystem: FakeFilesystem) -> None:
    """Test that symlink policy creates a symbolic link correctly."""
    # Arrange
    src_path = Path.cwd() / "dotfiles" / "test_file.conf"
    dst_path = Path.home() / ".config" / "test_file.conf"

    filesystem.create_file(src_path, contents=NORMAL_FILE_CONTENT)

    task = FileSyncTask(
        src=src_path,
        dst=dst_path,
        policy=FileSyncPolicy.SYMLINK,
    )

    syncer = FileSyncer(skip=True)
    record = ExecutionRecord.from_json(Path.cwd() / ".recnys" / "sync_record.json")

    # Act
    syncer.sync(tasks=[task], last_record=record)

    # Assert
    assert dst_path.exists(), f"Destination {dst_path} should exist"
    assert dst_path.is_symlink(), f"Destination {dst_path} should be a symlink"
    assert dst_path.resolve() == src_path.resolve(), (
        f"Symlink should point to {src_path}, but points to {dst_path.resolve()}"
    )


def test_symlink_policy_replaces_existing_file(filesystem: FakeFilesystem) -> None:
    """Test that symlink policy replaces an existing regular file."""
    # Arrange
    src_path = Path.cwd() / "dotfiles" / "test_file.conf"
    dst_path = Path.home() / ".config" / "test_file.conf"

    filesystem.create_file(src_path, contents=NORMAL_FILE_CONTENT)
    filesystem.create_file(dst_path, contents="old content")

    task = FileSyncTask(
        src=src_path,
        dst=dst_path,
        policy=FileSyncPolicy.SYMLINK,
    )

    syncer = FileSyncer(skip=True)
    record = ExecutionRecord.from_json(Path.cwd() / ".recnys" / "sync_record.json")

    # Act
    syncer.sync(tasks=[task], last_record=record)

    # Assert
    assert dst_path.exists(), f"Destination {dst_path} should exist"
    assert dst_path.is_symlink(), f"Destination {dst_path} should be a symlink"
    assert dst_path.resolve() == src_path.resolve(), (
        f"Symlink should point to {src_path}, but points to {dst_path.resolve()}"
    )


def test_symlink_policy_replaces_existing_symlink(filesystem: FakeFilesystem) -> None:
    """Test that symlink policy replaces an existing symlink."""
    # Arrange
    src_path = Path.cwd() / "dotfiles" / "test_file.conf"
    old_src_path = Path.cwd() / "dotfiles" / "old_file.conf"
    dst_path = Path.home() / ".config" / "test_file.conf"

    filesystem.create_file(src_path, contents=NORMAL_FILE_CONTENT)
    filesystem.create_file(old_src_path, contents="old content")
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    dst_path.symlink_to(old_src_path)

    task = FileSyncTask(
        src=src_path,
        dst=dst_path,
        policy=FileSyncPolicy.SYMLINK,
    )

    syncer = FileSyncer(skip=True)
    record = ExecutionRecord.from_json(Path.cwd() / ".recnys" / "sync_record.json")

    # Act
    syncer.sync(tasks=[task], last_record=record)

    # Assert
    assert dst_path.exists(), f"Destination {dst_path} should exist"
    assert dst_path.is_symlink(), f"Destination {dst_path} should be a symlink"
    assert dst_path.resolve() == src_path.resolve(), (
        f"Symlink should point to {src_path}, but points to {dst_path.resolve()}"
    )
