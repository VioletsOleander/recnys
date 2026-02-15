"""Provide `TaskExecutionDecision`, `TaskExecutionResult`, `TaskExecutionRecord` and `ExecutionRecord`."""

import dataclasses
import json
import logging
from collections.abc import Iterator, MutableMapping
from enum import StrEnum
from typing import TYPE_CHECKING

from .task import FileIOTask

if TYPE_CHECKING:
    from pathlib import Path


__all__ = ["ExecutionRecord", "TaskExecutionRecord"]

logger = logging.getLogger(__name__)


@dataclasses.dataclass(frozen=True)
class TaskExecutionDecision:
    """Decision on whether and why to execute a file I/O task.

    Attributes:
        ok (bool): Whether to execute the task.
        reason (str): Explanation for the decision.
    """

    ok: bool
    reason: str


class TaskExecutionResult(StrEnum):
    SUCCESS = "Success"
    SKIPPED = "Skipped"
    FAILURE = "Failure"


@dataclasses.dataclass(frozen=True, kw_only=True)
class TaskExecutionRecord:
    """Information about the execution of a file I/O task.

    Attributes:
        execution_decision (TaskExecutionDecision): The decision on whether and why to execute the task.
        execution_result (TaskExecutionResult): The result of the task execution.
        execution_time (str): The time when the task was executed.
        file_hash (str): The hash of the source file at the time of execution,
            used for change detection in future executions.
    """

    execution_decision: TaskExecutionDecision
    execution_result: TaskExecutionResult
    execution_time: str
    file_hash: str

    @classmethod
    def from_dict(cls, data: dict) -> TaskExecutionRecord:
        return cls(
            execution_decision=TaskExecutionDecision(**data["execution_decision"]),
            execution_result=TaskExecutionResult(data["execution_result"]),
            execution_time=data["execution_time"],
            file_hash=data["file_hash"],
        )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=4)


class ExecutionRecord(MutableMapping[FileIOTask, TaskExecutionRecord]):
    """Container for a batch of file I/O task execution records.

    Map FileIOTask to TaskExecutionRecord, allowing dict-like access and modification.

    Support serialization to and from specified JSON file.
    """

    _mapping: dict[FileIOTask, TaskExecutionRecord]

    def __init__(self) -> None:
        self._mapping = {}

    @classmethod
    def from_json(cls, file_path: Path) -> ExecutionRecord:
        """Load execution record from a JSON file.

        If the file does not exist, return an empty ExecutionRecord instance.

        Returns:
            ExecutionRecord: Loaded execution record instance.
        """
        execution_record = cls()
        if not file_path.exists():
            execution_record._mapping = {}
            logger.info(
                "Execution record file not found: %s, initialized an empty record.", file_path
            )
        else:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            execution_record._mapping = {
                FileIOTask(**k): TaskExecutionRecord.from_dict(v) for k, v in data.items()
            }
            logger.info("Loaded execution record from %s", file_path)

        return execution_record

    def save(self, file_path: Path) -> None:
        """Save the current execution record to the JSON file."""
        serializable_data = {
            dataclasses.asdict(k): dataclasses.asdict(v) for k, v in self._mapping.items()
        }

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=4)
        logger.info("Saved execution record to %s", file_path)

    def __getitem__(self, key: FileIOTask) -> TaskExecutionRecord:
        return self._mapping[key]

    def __setitem__(self, key: FileIOTask, value: TaskExecutionRecord) -> None:
        self._mapping[key] = value

    def __delitem__(self, key: FileIOTask) -> None:
        del self._mapping[key]

    def __iter__(self) -> Iterator[FileIOTask]:
        return iter(self._mapping)

    def __len__(self) -> int:
        return len(self._mapping)
