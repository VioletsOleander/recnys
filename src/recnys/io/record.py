"""Provide `TaskExecutionDecision`, `TaskExecutionResult`, `TaskExecutionRecord` and `ExecutionRecord`."""

import dataclasses
import json
import logging
from collections.abc import Iterator, MutableMapping
from enum import StrEnum
from typing import TYPE_CHECKING

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


class ExecutionRecord(MutableMapping[str, TaskExecutionRecord]):
    """Container for a batch of file I/O task execution records.

    Map str(FileIOTask.src) to TaskExecutionRecord, allowing dict-like access and modification.

    Support serialization to and from specified JSON file.

    Attributes:
        mapping (dict[str, TaskExecutionRecord]): The mapping from str(FileIOTask.src) to TaskExecutionRecord
    """

    mapping: dict[str, TaskExecutionRecord]

    def __init__(self) -> None:
        self.mapping = {}

    @classmethod
    def from_json(cls, file_path: Path) -> ExecutionRecord:
        """Load execution record from a JSON file.

        If the file does not exist, return an empty ExecutionRecord instance.

        Returns:
            ExecutionRecord: Loaded execution record instance.
        """
        execution_record = cls()
        if not file_path.exists():
            execution_record.mapping = {}
            logger.debug(
                "Execution record file not found: %s, initialized an empty record.", file_path
            )
        else:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            execution_record.mapping = {
                k: TaskExecutionRecord.from_dict(v) for k, v in data.items()
            }
            logger.debug("Loaded execution record from %s", file_path)

        return execution_record

    def save(self, file_path: Path) -> None:
        """Save the current execution record to the JSON file."""
        serializable_data = {k: dataclasses.asdict(v) for k, v in self.mapping.items()}

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=4)
        logger.debug("Saved execution record to %s", file_path)

    def __getitem__(self, key: str) -> TaskExecutionRecord:
        return self.mapping[key]

    def __setitem__(self, key: str, value: TaskExecutionRecord) -> None:
        self.mapping[key] = value

    def __delitem__(self, key: str) -> None:
        del self.mapping[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.mapping)

    def __len__(self) -> int:
        return len(self.mapping)
