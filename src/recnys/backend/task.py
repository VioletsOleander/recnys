"""Define `CanonicalSyncTask` and related data structures for describing canonicalized sync tasks."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.frontend.task import Policy, SyncTask

__all__ = ["CanonicalSyncTask", "canonicalize_sync_tasks"]


@dataclass(frozen=True)
class CanonicalSyncTask:
    """Description of a canonical synchronization task.

    A canonical synchronization task corresponds to a single file to be synchronized

    Attributes:
        src (Path): Path to the source of the synchronization.
        dst (Path): Path to the destination of the synchronization.
        policy (Policy): Policy of the synchronization.
    """

    src: Path
    dst: Path
    policy: Policy

    def __str__(self) -> str:
        return f"CanonicalSyncTask(src={self.src}, dst={self.dst}, policy={self.policy})"


def canonicalize_sync_tasks(sync_tasks: list[SyncTask]) -> list[CanonicalSyncTask]:
    """Canonicalize a list of sync tasks.

    Canonicalization means:
    - Expanding directory sync tasks into individual file sync tasks,
    - Removing sync tasks with None destinations.
        (i.e. files that are required not to be synced)
    - Deduplicating sync tasks, latter task overrides former one.

    Args:
        sync_tasks (list[SyncTask]): List of sync tasks to be canonicalized.

    Returns:
        list[CanonicalSyncTask]: List of canonicalized sync tasks.
    """
    canonicalized_tasks: dict[Path, CanonicalSyncTask] = {}
    for task in sync_tasks:
        if task.dst.path is None:
            continue

        # For file, just add it directly
        if not task.src.is_dir:
            canonicalized_tasks[task.src.path] = CanonicalSyncTask(
                src=task.src.path, dst=task.dst.path, policy=task.policy
            )
            continue

        # For directory, iterate through all files
        for file_path in task.src.path.rglob("*"):
            if not file_path.is_file():
                continue

            canonicalized_tasks[file_path] = CanonicalSyncTask(
                src=file_path,
                dst=task.dst.path / file_path.relative_to(task.src.path),
                policy=task.policy,
            )

    return list(canonicalized_tasks.values())
