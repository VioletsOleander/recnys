from pathlib import Path
from typing import TYPE_CHECKING

from recnys.linear.scanner import scan_variables
from recnys.tree.ctree.builder import CTreeBuilder
from recnys.tree.ctree.executor import CTreeExecutor
from recnys.tree.ctree.expander import CTreeExpander
from recnys.tree.dtree.builder import DTreeBuilder
from recnys.tree.dtree.executor import DTreeExecutor
from recnys.tree.model import CLeafOp, CTree, DTree
from recnys.tree.utils.serializer import deserialize_tree
from recnys.utils.context import ExecutionContext
from recnys.utils.loader import load_yaml

if TYPE_CHECKING:
    from recnys.linear.model import ScannedConfig


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
        ctree = self._grow_ctree(scanned_config)
        dtree = self._grow_dtree(ctree)

        if dtree is not None:
            executor = DTreeExecutor(dry_run=dry_run)
            with ExecutionContext(executor, self._dtree_file, dry_run=dry_run):
                executor.execute(dtree)

        if CLeafOp.RENDER in ctree.ops.values():
            loaded_variables = load_yaml(
                self._variables_file,
                note="Hint: Please run this command in the root of your dotfiles repository, "
                "where the variables.yaml file is located.",
            )
            variables = scan_variables(loaded_variables)
        else:
            variables = None

        executor = CTreeExecutor(variables=variables, dry_run=dry_run)
        with ExecutionContext(executor, self._ctree_file, dry_run=dry_run):
            executor.execute(ctree)

    def _grow_ctree(self, scanned_config: ScannedConfig) -> CTree:
        # Build ctree
        builder = CTreeBuilder()
        ctree = builder.build(scanned_config)

        # Expand ctree
        expander = CTreeExpander()
        return expander.expand(ctree)

    def _grow_dtree(self, ctree: CTree) -> DTree | None:
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
            prev_ctree = deserialize_tree(cls=CTree, f=self._ctree_file)
            prev_dtree = deserialize_tree(cls=DTree, f=self._dtree_file)
            builder = DTreeBuilder()
            return builder.build(ctree, prev_ctree, prev_dtree)

        return None

    def _arrange(self) -> None:
        data_dir = Path.home() / ".recnys"
        self._ctree_file = data_dir / "prev_ctree.json"
        self._dtree_file = data_dir / "prev_dtree.json"
        self._variables_file = data_dir / "variables.yaml"

        data_dir.mkdir(exist_ok=True)
        gitignore = data_dir / ".gitignore"
        if not gitignore.exists():
            gitignore.write_text("# Created by recnys\n*\n", encoding="utf-8")
