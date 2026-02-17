"""Provide `FileIOTaskExecutor` and execution related data structures."""

from __future__ import annotations

import logging
from abc import abstractmethod
from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from .record import ExecutionRecord, TaskExecutionDecision, TaskExecutionRecord, TaskExecutionResult
from .task import FileIOTask
from .utils import get_normalized_file_hash

logger = logging.getLogger(__name__)

__all__ = ["FileIOTaskExecutor"]


class FileIOTaskExecutor[T_contra: FileIOTask](Protocol):
    """The executor of file I/O tasks.

    The executor is able to make execution decisions and execute
    file I/O tasks sequentially, while maintaining an execution record.

    The implementing class is required to implement `_execute_task` method, which
    executes the file I/O task based on the execution decision.
    """

    @abstractmethod
    def _execute_task(self, task: T_contra, decision: TaskExecutionDecision) -> TaskExecutionResult:
        """Execute the file I/O task based on the execution decision.

        Args:
            task (T_contra): The file I/O task to be executed.
            decision (TaskExecutionDecision): The decision on whether and why to execute the task.

        Returns:
            TaskExecutionResult: The result of the task execution.
        """

    def execute(self, tasks: Sequence[T_contra], last_record: ExecutionRecord) -> ExecutionRecord:
        """Execute given file I/O tasks sequentially.

        Args:
            tasks (Sequence[T_contra]): Sequence of file I/O tasks to be executed.
            last_record (ExecutionRecord): Record of last execution of the tasks,
                used for making execution decisions.

        Returns:
            ExecutionRecord: Record of the execution process of the given tasks.
        """
        record = ExecutionRecord()

        for task in tasks:
            logger.debug("Executing task: %s", task)

            key = str(task.src)
            decision = self._make_execution_decision(
                task=task, last_task_record=last_record.get(key)
            )
            result = self._execute_task(task=task, decision=decision)
            record[key] = self._make_execution_record(task=task, decision=decision, result=result)

            logger.debug("Finished executing task: %s", task)

        return record

    def _make_execution_decision(
        self, task: T_contra, last_task_record: TaskExecutionRecord | None
    ) -> TaskExecutionDecision:
        """Make execution decision for a file I/O task based on the last execution record.

        Args:
            task (T_contra): The file I/O task for which to make the execution decision.
            last_task_record (TaskExecutionRecord | None): The record of the last execution of the task,
                used for making the decision, or None if the task has never been executed before.

        Returns:
            TaskExecutionDecision: The decision on whether and why to execute the task.
        """
        if task.force_execute:
            return TaskExecutionDecision(
                ok=True,
                reason=f"Task '{task.name}' is forced to execute, ignoring execution decisions",
            )

        if last_task_record is None:
            return TaskExecutionDecision(
                ok=True,
                reason=f"There is no previous execution record for task '{task.name}',"
                " need to execute the task to generate the target file"
                " and create the record for future reference",
            )

        if not task.dst.exists():
            return TaskExecutionDecision(
                ok=True,
                reason=f"The target file for task '{task.name}' does not exist,"
                " need to execute the task to create the target file",
            )

        curr_hash = get_normalized_file_hash(file_path=task.src)
        prev_hash = last_task_record.file_hash
        if prev_hash != curr_hash:
            return TaskExecutionDecision(
                ok=True,
                reason=f"The source file for task '{task.name}' is modified since last execution,"
                " need to re-execute the task to update the target file",
            )

        src_hash = curr_hash
        dst_hash = get_normalized_file_hash(file_path=task.dst)
        if src_hash != dst_hash:
            return TaskExecutionDecision(
                ok=True,
                reason=f"The target file for task '{task.name}' is modified since last execution,"
                " need to re-execute the task to update the target file",
            )

        return TaskExecutionDecision(
            ok=False,
            reason=f"The source and target files for task '{task.name}' are unchanged,"
            " skipping task execution",
        )

    def _make_execution_record(
        self, task: T_contra, decision: TaskExecutionDecision, result: TaskExecutionResult
    ) -> TaskExecutionRecord:
        """Make execution record for a file I/O task based on the execution decision and result."""
        timestamp = datetime.now().isoformat()
        file_hash = get_normalized_file_hash(task.src)
        return TaskExecutionRecord(
            execution_decision=decision,
            execution_result=result,
            execution_time=timestamp,
            file_hash=file_hash,
        )
