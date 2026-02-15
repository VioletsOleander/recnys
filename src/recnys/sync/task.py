from dataclasses import dataclass
from enum import StrEnum

from recnys.io.task import FileIOTask

__all__ = ["FileSyncPolicy", "FileSyncTask"]


class FileSyncPolicy(StrEnum):
    """Policy of a file synchronization task.

    Attributes:
        COPY: Copy source contents to destination, replacing existing content.
        SOURCE: Prepend a "source" statement to existing content.
        DEFAULT: Default policy (COPY).
    """

    COPY = "copy"
    SOURCE = "source"
    DEFAULT = COPY

    @property
    def description(self) -> str:
        """Get a human-readable description of the policy."""
        match self:
            case FileSyncPolicy.COPY:
                return "Copy contents"
            case FileSyncPolicy.SOURCE:
                return 'Prepend a "source" statement'


@dataclass(frozen=True, kw_only=True)
class FileSyncTask(FileIOTask):
    """Representation of a file synchronization task.

    See `FileIOTask` for more details.

    Attributes:
        name (str): "File Sync" by default.
        policy (FileSyncPolicy): Policy of the synchronization.
    """

    name: str = "File Sync"
    policy: FileSyncPolicy

    def __str__(self) -> str:
        return f"FileSyncTask(src={self.src}, dst={self.dst}, policy={self.policy})"
