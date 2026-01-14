"""Provide `Syncer` to execute sync tasks and manage sync state."""

import logging
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from recnys.frontend.task import Policy
from recnys.frontend.task import SyncTask as RawSyncTask

from .state import SyncDecision, TaskSyncState
from .task import CanonicalSyncTask as SyncTask
from .task import canonicalize_sync_tasks
from .utils import get_file_hash, prompt_for_confirmation

if TYPE_CHECKING:
    from pathlib import Path

    from .state import SyncState


__all__ = ["Syncer"]

logger = logging.getLogger(__name__)


def _make_sync_decision(task: SyncTask, state: SyncState) -> SyncDecision:
    """Determine the sync decision for a given sync task based on current state.

    Args:
        task (SyncTask): The sync task to evaluate.
        state (SyncState): The current sync state.

    Returns:
        SyncDecision: The decision on how to handle the sync task.
    """
    src = task.src
    dst = task.dst

    task_sync_state = state.get(src)
    if task_sync_state is None:
        return SyncDecision.NEW_FILE

    curr_hash = get_file_hash(task.src)
    prev_hash = task_sync_state.file_hash
    if prev_hash != curr_hash:
        return SyncDecision.SRC_MODIFIED

    if not dst.exists():
        return SyncDecision.DST_MISSING

    match task.policy:
        case Policy.SOURCE:
            expected_statement = f'source "{src}"\n'
            with dst.open("r", encoding="utf-8") as f:
                first_line = f.readline()
            if not first_line or first_line != expected_statement:
                return SyncDecision.DST_MODIFIED
        case Policy.OVERWRITE:
            src_hash = curr_hash
            dst_hash = get_file_hash(dst)
            if src_hash != dst_hash:
                return SyncDecision.DST_MODIFIED

    return SyncDecision.SKIP


def _make_task_sync_state(task: SyncTask, decision: SyncDecision) -> TaskSyncState:
    """Create a new TaskSyncState based on given the sync task and decision."""
    timestamp = datetime.now().isoformat()
    file_hash = get_file_hash(task.src)
    return TaskSyncState(
        dst=str(task.dst), file_hash=file_hash, last_sync_time=timestamp, sync_decision=decision
    )


class _ExecutionResult(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


class Syncer:
    """Synchronize files and manage sync state.

    Attributes:
        sync_tasks (list[SyncTask]): List of sync tasks to perform.
        sync_state (SyncState): Current state of synchronization.
    """

    sync_tasks: list[SyncTask]
    sync_state: SyncState

    def __init__(self, sync_state: SyncState, sync_tasks: list[RawSyncTask]) -> None:
        self.sync_state = sync_state
        self.sync_tasks = canonicalize_sync_tasks(sync_tasks)

    def sync(self, *, force: bool = False) -> SyncState:
        """Perform the sync operations for all sync tasks.

        Updates the sync state after each successful sync.

        Args:
            force (bool): If True, skip user confirmation prompts.

        Returns:
            SyncState: The updated sync state after performing sync operations.
        """
        for task in self.sync_tasks:
            decision = _make_sync_decision(task, self.sync_state)

            if decision == SyncDecision.SKIP:
                logger.info("Skipping sync for %s", task.src)
                continue

            logger.info("Syncing %s with reason %s", task.src, decision.value)
            if Syncer._execute_sync_task(task, force=force) == _ExecutionResult.SUCCESS:
                self.sync_state[task.src] = _make_task_sync_state(task, decision)
                logger.info("Updated sync state for %s", task.src)

        return self.sync_state

    @staticmethod
    def _execute_sync_task(task: SyncTask, *, force: bool = False) -> _ExecutionResult:
        """Execute the sync task by syncing the source file to a temporary destination.

        This is an atomic operation, if the sync fails, the original destination file remains unchanged.

        Args:
            task (SyncTask): The sync task to execute.
            force (bool): If True, skip user confirmation prompts.

        Returns:
            _ExecutionResult: The result of the sync operation.
        """
        tmp_dst = task.dst.with_suffix(task.dst.suffix + ".tmp_sync")

        try:
            Syncer._sync_file(src=task.src, dst=tmp_dst, policy=task.policy, force=force)
            tmp_dst.replace(task.dst)
            logger.info("Successfully synced file %s to %s", task.src, task.dst)
        except Exception:
            logger.exception("Failed to sync file %s to %s", task.src, task.dst)
            return _ExecutionResult.FAILURE
        else:
            return _ExecutionResult.SUCCESS
        finally:
            tmp_dst.unlink(missing_ok=True)
            logger.info("Cleaned up temporary file %s", tmp_dst)

    @staticmethod
    def _sync_file(src: Path, dst: Path, policy: Policy, *, force: bool = False) -> None:
        """Sync a single file from src to dst according to the specified policy.

        Args:
            src (Path): Source file path.
            dst (Path): Destination file path.
            policy (Policy): Sync policy to apply.
            force (bool): If True, skip user confirmation prompts.
        """
        prompt = (
            f"{policy.capitalize} to existing file: {dst}?\n"
            if dst.exists()
            else f"Destination file does not exist. Create {dst} and copy content?\n"
        )
        prompt = prompt + "(Press Enter to confirm, and any other key to refuse): "

        if not force and not prompt_for_confirmation(message=prompt, confirm_signals=("")):
            logger.info("User declined to %s to %s", policy.lower(), dst)
            return

        match policy:
            case Policy.OVERWRITE:
                content = src.read_text(encoding="utf-8")
            case Policy.SOURCE:
                origin_content = dst.open("r", encoding="utf-8").read() if dst.exists() else ""
                source_statement = f'source "{src}"'
                content = source_statement + "\n\n" + origin_content

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(content, encoding="utf-8")
        logger.info("Successfully %s to %s", policy.lower(), dst)
