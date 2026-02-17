from __future__ import annotations

from pathlib import Path

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.io.record import ExecutionRecord, TaskExecutionResult
from recnys.sync.task import FileSyncPolicy, FileSyncTask
from recnys.testing.build.arrange import make_sync_tasks
from recnys.testing.sync.arrange import create_source_files, make_sync_record, make_syncer
from recnys.testing.sync.asserting import assert_sync_record_io, assert_synced_correctly


def test_sync(system: str, filesystem: FakeFilesystem) -> None:
    """Test syncing when destination files don't exist."""
    sync_tasks = make_sync_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    record = make_sync_record()
    syncer = make_syncer()

    record = syncer.sync(tasks=sync_tasks, last_record=record)

    assert_synced_correctly(tasks=sync_tasks)
    assert_sync_record_io(sync_record=record)


def test_sync_with_existing_destination_copy_policy(
    system: str, filesystem: FakeFilesystem
) -> None:
    """Test syncing when destination files already exist with COPY policy.

    The destination file should be overwritten with source content.
    """
    # Create tasks with only COPY policy (filter out SOURCE policy)
    all_tasks = make_sync_tasks(system=system)
    sync_tasks = [task for task in all_tasks if task.policy == FileSyncPolicy.COPY]

    create_source_files(filesystem=filesystem, tasks=sync_tasks)

    # Create existing destination files with different content
    for task in sync_tasks:
        task.dst.parent.mkdir(parents=True, exist_ok=True)
        task.dst.write_text("Old content that should be replaced", encoding="utf-8")

    record = make_sync_record()
    syncer = make_syncer()

    record = syncer.sync(tasks=sync_tasks, last_record=record)

    # Verify all files were synced correctly (old content replaced)
    assert_synced_correctly(tasks=sync_tasks)
    assert_sync_record_io(sync_record=record)

    # Verify all tasks succeeded
    for task in sync_tasks:
        task_record = record[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SUCCESS


def test_sync_with_existing_destination_source_policy(
    system: str, filesystem: FakeFilesystem
) -> None:
    """Test syncing with SOURCE policy when destination already exists.

    The source statement should be prepended to existing content.
    """
    # Create a simple task with SOURCE policy
    src_path = Path.cwd() / "test.sh"
    dst_path = Path.home() / ".bashrc"

    filesystem.create_file(src_path, contents="# Source script")

    # Create existing destination with some content
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    existing_content = "# Existing bashrc content\necho 'Hello'"
    dst_path.write_text(existing_content, encoding="utf-8")

    task = FileSyncTask(src=src_path, dst=dst_path, policy=FileSyncPolicy.SOURCE)

    record = ExecutionRecord()
    syncer = make_syncer()

    record = syncer.sync(tasks=[task], last_record=record)

    # Verify the source statement was prepended
    result_content = dst_path.read_text(encoding="utf-8")
    expected_content = f'source "{src_path}"\n\n{existing_content}'
    assert result_content == expected_content, (
        f"Expected SOURCE policy to prepend source statement. "
        f"Expected: {expected_content!r}, Got: {result_content!r}"
    )

    # Verify task succeeded
    task_record = record[str(task.src)]
    assert task_record.execution_result == TaskExecutionResult.SUCCESS


def test_sync_skips_unchanged_files(system: str, filesystem: FakeFilesystem) -> None:
    """Test that syncing skips files when both source and destination are unchanged."""
    # Only test with COPY policy, as SOURCE policy always modifies destination
    all_tasks = make_sync_tasks(system=system)
    sync_tasks = [task for task in all_tasks if task.policy == FileSyncPolicy.COPY]

    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    syncer = make_syncer()

    # First sync - creates all files
    record1 = make_sync_record()
    record1 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Verify all files were created successfully
    for task in sync_tasks:
        task_record = record1[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SUCCESS

    # Second sync with same files - should skip
    record2 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Verify all tasks were skipped
    for task in sync_tasks:
        task_record = record2[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SKIPPED, (
            f"Expected task {task.src} to be skipped, "
            f"but got result: {task_record.execution_result}"
        )


def test_sync_updates_when_source_changes(system: str, filesystem: FakeFilesystem) -> None:
    """Test that syncing updates destination when source file changes."""
    sync_tasks = make_sync_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    syncer = make_syncer()

    # First sync
    record1 = make_sync_record()
    record1 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Modify source files
    for task in sync_tasks:
        task.src.write_text("Modified source content", encoding="utf-8")

    # Second sync - should update because source changed
    record2 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Verify all tasks succeeded (not skipped)
    for task in sync_tasks:
        task_record = record2[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SUCCESS, (
            f"Expected task {task.src} to succeed after source change, "
            f"but got result: {task_record.execution_result}"
        )

        # Verify destination was updated
        dst_content = task.dst.read_text(encoding="utf-8")
        if task.policy == FileSyncPolicy.COPY:
            assert "Modified source content" in dst_content
        # For SOURCE policy, the modified content should be in the source statement context


def test_sync_updates_when_destination_changes(
    system: str, filesystem: FakeFilesystem
) -> None:
    """Test that syncing updates destination when destination file is modified."""
    # Only test with COPY policy, as SOURCE policy always modifies destination
    all_tasks = make_sync_tasks(system=system)
    sync_tasks = [task for task in all_tasks if task.policy == FileSyncPolicy.COPY]

    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    syncer = make_syncer()

    # First sync
    record1 = make_sync_record()
    record1 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Modify destination files manually (simulating external changes)
    for task in sync_tasks:
        task.dst.write_text("Manually modified destination", encoding="utf-8")

    # Second sync - should update because destination changed
    record2 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Verify all tasks succeeded (not skipped)
    for task in sync_tasks:
        task_record = record2[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SUCCESS, (
            f"Expected task {task.src} to succeed after destination change, "
            f"but got result: {task_record.execution_result}"
        )

    # Verify destinations were restored from source
    assert_synced_correctly(tasks=sync_tasks)


def test_sync_with_force_execute(system: str, filesystem: FakeFilesystem) -> None:
    """Test that force_execute flag forces sync even when files are unchanged."""
    sync_tasks = make_sync_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=sync_tasks)
    syncer = make_syncer()

    # First sync
    record1 = make_sync_record()
    record1 = syncer.sync(tasks=sync_tasks, last_record=record1)

    # Create new tasks with force_execute=True
    force_tasks = [
        FileSyncTask(
            src=task.src,
            dst=task.dst,
            policy=task.policy,
            force_execute=True,
        )
        for task in sync_tasks
    ]

    # Second sync with force_execute - should execute even though files unchanged
    record2 = syncer.sync(tasks=force_tasks, last_record=record1)

    # Verify all tasks succeeded (not skipped)
    for task in force_tasks:
        task_record = record2[str(task.src)]
        assert task_record.execution_result == TaskExecutionResult.SUCCESS, (
            f"Expected task {task.src} to succeed with force_execute, "
            f"but got result: {task_record.execution_result}"
        )
