"""Provide `Syncer` to execute sync tasks and manage sync state."""

import logging
from typing import TYPE_CHECKING, override

from recnys.io.executor import FileIOTaskExecutor
from recnys.io.record import TaskExecutionDecision, TaskExecutionResult

from .task import FileSyncPolicy, FileSyncTask
from .utils import prompt_for_confirmation

if TYPE_CHECKING:
    from recnys.io.record import ExecutionRecord

__all__ = ["FileSyncer"]

logger = logging.getLogger(__name__)


class FileSyncer(FileIOTaskExecutor[FileSyncTask]):
    """FileSyncer is responsible for executing file synchronization tasks.

    It implements FileIOTaskExecutor, which allows it to make execution decisions and execute
    file I/O tasks sequentially, while maintaining an execution record.

    The main provided method is `sync`.
    """

    _skip: bool

    def __init__(self, *, skip: bool = False) -> None:
        """Initialize the FileSyncer.

        Args:
            skip (bool): If True, skip user confirmation prompts during sync operations.
        """
        self._skip = skip

    def sync(self, tasks: list[FileSyncTask], last_record: ExecutionRecord) -> ExecutionRecord:
        """Execute the file synchronization tasks sequentially, while maintaining an execution record.

        Args:
            tasks (list[FileSyncTask]): The list of file synchronization tasks to be executed.
            last_record (ExecutionRecord): The execution record of the last execution.

        Returns:
            ExecutionRecord: The execution record of the current execution,
                which will be used for future reference
        """
        return self.execute(tasks, last_record)

    def _execute_sync_task(self, task: FileSyncTask) -> TaskExecutionResult:
        """Execute the file synchronization task."""
        tmp_dst = None
        try:
            logger.info(
                "Syncing file %s to %s with policy '%s'...", task.src, task.dst, task.policy
            )
            task.dst.parent.mkdir(parents=True, exist_ok=True)

            if task.policy == FileSyncPolicy.SYMLINK:
                # Remove existing file or symlink if it exists
                if task.dst.exists() or task.dst.is_symlink():
                    task.dst.unlink()
                # Create symbolic link pointing to source
                task.dst.symlink_to(task.src)
                logger.info("Successfully created symlink %s -> %s", task.dst, task.src)
            else:
                match task.policy:
                    case FileSyncPolicy.COPY:
                        content = task.src.read_text(encoding="utf-8")
                    case FileSyncPolicy.SOURCE:
                        origin_content = (
                            task.dst.read_text(encoding="utf-8") if task.dst.exists() else ""
                        )
                        source_statement = f'source "{task.src}"'
                        content = source_statement + "\n\n" + origin_content

                tmp_dst = task.dst.with_suffix(task.dst.suffix + ".tmp_sync")
                tmp_dst.write_text(content, encoding="utf-8")
                tmp_dst.replace(task.dst)
                logger.info("Successfully synced file %s to %s", task.src, task.dst)
        except Exception:
            logger.exception("Failed to sync file %s to %s", task.src, task.dst)
            return TaskExecutionResult.FAILURE
        else:
            return TaskExecutionResult.SUCCESS
        finally:
            if tmp_dst is not None:
                tmp_dst.unlink(missing_ok=True)
                logger.debug("Cleaned up temporary file %s", tmp_dst)

    @override
    def _execute_task(
        self, task: FileSyncTask, decision: TaskExecutionDecision
    ) -> TaskExecutionResult:
        """Execute the file synchronization task based on the execution decision."""
        if decision.ok is False:
            logger.debug(
                "Skipping synchronization for %s based on decision: %s", task.src, decision.reason
            )
            return TaskExecutionResult.SKIPPED

        if task.dst.exists():
            prompt = (
                f"> Do you want to execute action: '{task.policy.description}'"
                f" to existing file: {task.dst}?\n"
            )
        else:
            prompt = (
                f"> Do you want to execute action: '{task.policy.description}'"
                f" to create new file: {task.dst}?\n"
            )
        prompt = prompt + "(Press Enter to confirm, and any other key to refuse): "

        if not self._skip and not prompt_for_confirmation(message=prompt, confirm_signal=""):
            logger.info("Received denial from user, skipping sync for %s", task.src)
            return TaskExecutionResult.SKIPPED

        return self._execute_sync_task(task)
