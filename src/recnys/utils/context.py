import logging
from contextlib import AbstractContextManager
from typing import TYPE_CHECKING, Self, override

from recnys.tree.utils.serializer import serialize_tree

if TYPE_CHECKING:
    from pathlib import Path
    from types import TracebackType

    from recnys.tree.ctree.executor import CTreeExecutor
    from recnys.tree.dtree.executor import DTreeExecutor


logger = logging.getLogger(__name__)

__all__ = ["ExecutionContext"]


class ExecutionContext(AbstractContextManager):
    """Context manager for executing a tree.

    Attributes:
        executor (DTreeExecutor | CTreeExecutor): The executor to execute the tree.
        tree_file (Path): The file path for storing the tree after execution.
        dry_run (bool): Whether to perform a dry run of the execution.
    """

    executor: DTreeExecutor | CTreeExecutor
    tree_file: Path
    dry_run: bool

    def __init__(
        self, executor: DTreeExecutor | CTreeExecutor, tree_file: Path, *, dry_run: bool
    ) -> None:
        """Initialize the ExecutionContext.

        Args:
            executor (DTreeExecutor | CTreeExecutor): The executor to execute the tree.
            tree_file (Path): The file path for storing the tree after execution.
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.executor = executor
        self.tree_file = tree_file
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
        if self.dry_run:
            logger.debug("Execution context exited with dry run, no tree will be saved")
            return False

        logger.debug("Execution context exiting, saving the tree to files")

        f = self.tree_file
        serialize_tree(self.executor.tree, f)
        logger.debug("Tree saved to %s", f)

        f_backup = f.with_suffix(f.suffix + ".backup")
        f.copy(f_backup)
        logger.debug("Backup of the tree saved to %s", f_backup)

        logger.debug("Execution context exited")
        return False
