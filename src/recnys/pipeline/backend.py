import logging
from contextlib import AbstractContextManager
from pathlib import Path
from typing import TYPE_CHECKING, Self, override

from recnys.linear.scanner import scan_variables
from recnys.tree.ctree.builder import CTreeBuilder
from recnys.tree.ctree.executor import CTreeExecutor
from recnys.tree.ctree.expander import CTreeExpander
from recnys.tree.dtree.builder import DTreeBuilder
from recnys.tree.dtree.executor import DTreeExecutor
from recnys.tree.model import BranchNode, CLeafOp, CTree, DTree
from recnys.tree.utils.serializer import deserialize_tree, serialize_tree

from .loader import load_yaml

if TYPE_CHECKING:
    from types import TracebackType

    from recnys.linear.model import ScannedConfig, ScannedVariables

__all__ = ["BackendPipeline"]

logger = logging.getLogger(__name__)


class BackendPipeline:
    """BackendPipeline orchestrates the backend pipeline.

    The backend pipeline includes growing the creation tree and the deletion tree, and executing them.

    The main provided method is `run`.
    """

    _ctree_file: Path
    _dtree_file: Path
    _variables_file: Path

    def __init__(self) -> None:
        """Initialize the BackendPipeline, preparing necessary resources for the pipeline execution."""
        self._arrange()

    def run(self, scanned_config: ScannedConfig, *, dry_run: bool) -> None:
        """Run the backend pipeline.

        Args:
            scanned_config (ScannedConfig): The scanned configuration from the frontend pipeline.
            dry_run (bool): Whether to perform a dry run of the execution. If True, the execution will only
                log the operations without actually performing them.
        """
        logger.debug("Running backend pipeline.")

        ctree = self._grow_ctree(scanned_config)
        dtree = self._grow_dtree(ctree)

        d_executor = DTreeExecutor(dry_run=dry_run)
        with _ExecutionContent(d_executor, self._dtree_file, dry_run=dry_run):
            d_executor.execute(dtree)

        variables = self._get_variables(ctree)
        c_executor = CTreeExecutor(variables=variables, dry_run=dry_run)
        with _ExecutionContent(c_executor, self._ctree_file, dry_run=dry_run):
            c_executor.execute(ctree)

        num_ops = c_executor.num_executed_ops + d_executor.num_executed_ops
        if num_ops == 0:
            verb = "would be executed" if dry_run else "to execute"
            logger.info("Everything is up to date, no operations %s.", verb)
        else:
            verb = "would complete" if dry_run else "completed"
            logger.info("Execution %s with %d operations executed.", verb, num_ops)

        logger.debug("Finished running backend pipeline.")

    def _grow_ctree(self, scanned_config: ScannedConfig) -> CTree:
        # Build ctree
        builder = CTreeBuilder()
        ctree = builder.build(scanned_config)

        # Expand ctree
        expander = CTreeExpander()
        return expander.expand(ctree)

    def _grow_dtree(self, ctree: CTree) -> DTree:
        # Build dtree
        ctree_fexist = self._ctree_file.exists()
        dtree_fexist = self._dtree_file.exists()

        # Both not exist -> first run -> execute ctree
        # Both exist -> no-first run -> execute dtree, then ctree
        if ctree_fexist != dtree_fexist:
            e = RuntimeError(
                "Ctree file and dtree file are not consistent. "
                f"Please ensure that both {self._ctree_file} and {self._dtree_file} exist, "
                "or both of them do not exist."
            )
            e.add_note(
                "Hint: If backup files are available, please use them to recover the missing file. "
                "Otherwise, delete the existing file."
            )
            raise e

        if ctree_fexist:
            logger.debug("Previous ctree and dtree found.")

            prev_ctree = deserialize_tree(cls=CTree, f=self._ctree_file)
            prev_dtree = deserialize_tree(cls=DTree, f=self._dtree_file)
            builder = DTreeBuilder()
            dtree = builder.build(ctree, prev_ctree, prev_dtree)
        else:
            dtree = DTree(root=BranchNode(dst=Path.home()))
            logger.debug("No previous ctree and dtree found, build an empty root dtree.")

        return dtree

    def _get_variables(self, ctree: CTree) -> ScannedVariables | None:
        if CLeafOp.RENDER in ctree.ops.values():
            loaded_variables = load_yaml(
                self._variables_file,
                note="Hint: Please run this command in the root of your dotfiles repository, "
                "where the variables.yaml file is located.",
            )
            return scan_variables(loaded_variables)

        return None

    def _arrange(self) -> None:
        self._variables_file = Path.cwd() / "variables.yaml"
        self._ctree_file = Path.cwd() / ".recnys" / "prev_ctree.json"
        self._dtree_file = Path.cwd() / ".recnys" / "prev_dtree.json"


class _ExecutionContent(AbstractContextManager):
    """Context manager for executing a tree."""

    executor: DTreeExecutor | CTreeExecutor
    tree_file: Path
    dry_run: bool

    def __init__(
        self, executor: DTreeExecutor | CTreeExecutor, tree_file: Path, *, dry_run: bool
    ) -> None:
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

        parent = self.tree_file.parent
        parent.mkdir(exist_ok=True)

        ignore = parent / ".gitignore"
        if not ignore.exists():
            ignore.write_text("# Created by recnys\n*\n", encoding="utf-8")

        f = self.tree_file
        serialize_tree(self.executor.tree, f)
        logger.debug("Tree saved to %s", f)

        f_backup = f.with_suffix(f.suffix + ".backup")
        f.copy(f_backup)
        logger.debug("Backup of the tree saved to %s", f_backup)

        logger.debug("Execution context exited")
        return False
