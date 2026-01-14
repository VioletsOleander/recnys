"""Provide `SyncState` for managing synchronization state."""

import dataclasses
import json
import logging
from collections.abc import Iterator, MutableMapping
from enum import StrEnum
from pathlib import Path
from typing import override

__all__ = ["SyncDecision", "SyncState", "TaskSyncState"]

logger = logging.getLogger(__name__)


class SyncDecision(StrEnum):
    SKIP = "Update to date, skip synchronization"
    NEW_FILE = "New file to be synchronized"
    SRC_MODIFIED = "Source File is modified (hash mismatch) since last sync"
    DST_MISSING = "Destination file does not exist or is deleted since last sync"
    DST_MODIFIED = "Destination file is modified (hash mismatch) since last sync"
    NO_SOURCE_STATEMENT = "Destination file but not have a 'source' statement on top"


@dataclasses.dataclass(frozen=True)
class TaskSyncState:
    """State entry for a canonical synchronization task.

    Attributes:
        dst (str): Destination file path.
        file_hash (str): Hash of the synchronized file.
        last_sync_time (str): Timestamp of the last synchronization.
        sync_decision (SyncDecision): Decision made during the last sync.
    """

    dst: str
    file_hash: str
    last_sync_time: str
    sync_decision: SyncDecision

    @classmethod
    def from_dict(cls, data: dict) -> TaskSyncState:
        return cls(
            dst=data["dst"],
            file_hash=data["file_hash"],
            last_sync_time=data["last_sync_time"],
            sync_decision=SyncDecision(data["sync_decision"]),
        )

    def __str__(self) -> str:
        return json.dumps(dataclasses.asdict(self), indent=4)


@dataclasses.dataclass
class SyncState(MutableMapping[Path, TaskSyncState]):
    """Container for the state of the synchronization process.

    Map task source paths (`Path`) to their synchronization states (`TaskSyncState`).
    Allow dict-like access and modification.

    Support serialization to and from specified JSON file.
    """

    _state: dict[str, TaskSyncState] = dataclasses.field(init=False, default_factory=dict)

    @classmethod
    def from_json(cls, file_path: Path) -> SyncState:
        """Load sync state from a JSON file.

        If the file does not exist, return an empty SyncState instance.

        Returns:
            SyncState: Loaded sync state instance.
        """
        sync_state = cls()
        if not file_path.exists():
            logger.info("Sync state file not found: %s, initializing an empty state.", file_path)
        else:
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            sync_state._state = {k: TaskSyncState.from_dict(v) for k, v in data.items()}
            logger.info("Loaded sync state from %s", file_path)

        return sync_state

    def save(self, file_path: Path) -> None:
        """Save the current sync state to the JSON file."""
        serializable_data = {k: dataclasses.asdict(v) for k, v in self._state.items()}

        with file_path.open("w", encoding="utf-8") as f:
            json.dump(serializable_data, f, indent=4)
        logger.info("Saved sync state to %s", file_path)

    @override
    def __getitem__(self, task_src: Path) -> TaskSyncState:
        return self._state[str(task_src)]

    @override
    def __setitem__(self, task_src: Path, task_sync_state: TaskSyncState) -> None:
        self._state[str(task_src)] = task_sync_state

    @override
    def __delitem__(self, task_src: Path) -> None:
        del self._state[str(task_src)]

    @override
    def __iter__(self) -> Iterator[Path]:
        return map(Path, iter(self._state))

    @override
    def __len__(self) -> int:
        return len(self._state)
