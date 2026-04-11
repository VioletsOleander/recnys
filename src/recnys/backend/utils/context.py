import logging
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Self, override

from recnys.backend.dtree.executor import DTreeExecutor
from recnys.backend.utils.serializer import serialize_tree

if TYPE_CHECKING:
    from types import TracebackType

    from recnys.utils.paths import Paths

logger = logging.getLogger(__name__)


class ExecutionContext(AbstractContextManager):
    """Context manager for executing a tree.

    Attributes:
        executor: The DTreeExecutor instance that is executing the tree.
        paths: The Paths instance that contains the file paths for the dtree and its backup.
        dry_run: Whether to perform a dry run of the execution.
    """

    executor: DTreeExecutor
    paths: Paths
    dry_run: bool

    def __init__(self, executor: DTreeExecutor, paths: Paths, *, dry_run: bool) -> None:
        self.executor = executor
        self.paths = paths
        self.dry_run = dry_run

    def __enter__(self) -> Self:
        logger.debug("Execution context entered")
        return self

    @override
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        if isinstance(self.executor, DTreeExecutor):
            if self.dry_run:
                logger.debug("Execution context exited, dry run, no changes made")
                return False

            f = self.paths.dtree_file
            f_backup = self.paths.dtree_backup_file

            serialize_tree(self.executor.dtree, f)
            f.copy(f_backup)

            logger.debug(
                "Execution context exited, dtree saved to %s and backup saved to %s", f, f_backup
            )

        return False
