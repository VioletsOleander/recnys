"""Provide `DTreeExecutor`."""

import logging
from typing import TYPE_CHECKING

from recnys.backend.model import BranchNode, DBranchOp, DLeafOp, DTree, LeafNode, Node
from recnys.backend.utils.collector import collect_nodes
from recnys.backend.utils.walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["DTreeExecutor"]

logger = logging.getLogger(__name__)


class DTreeExecutor:
    """DTreeExecutor executes a deletion tree.

    The main provided method is `execute`.

    Attributes:
        dtree (RootNode): The root node of the deletion tree after execution.
        dry_run (bool): Whether to perform a dry run of the execution.
            If True, the execution will only log the operations without actually performing them.
    """

    dry_run: bool

    def __init__(self, *, dry_run: bool) -> None:
        """Initialize the DTreeExecutor.

        Args:
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.dry_run = dry_run

    def execute(self, dtree: DTree) -> DTree:
        """Execute the given dtree.

        Return a new dtree with the executed nodes detached from the tree. If all nodes are executed
        successfully, the returned dtree will be an root node with no children.

        Args:
            dtree (RootNode): The root node of the deletion tree to be executed.

        Returns:
            RootNode: The root node of the deletion tree with the executed nodes detached from the tree
        """
        tree = dtree.model_copy(deep=True)
        parents = collect_nodes(tree, collect_leaf=False)
        ops = tree.ops

        def detach_node(node: Node) -> None:
            parent = parents[node.dst.parent]
            parent.children.pop(node.dst)
            ops.pop(node.dst)

        def execute_branch(node: BranchNode) -> None:
            """Execute deletion op (nop or remove) on branch node (dir).

            Detach the node after execution.
            """
            if ops[node.dst] == DBranchOp.REMOVE:
                self._rmdir(node.dst)

            return detach_node(node)

        def execute_leaf(node: LeafNode) -> None:
            """Execute deletion op (nop or unlink) on leaf node (file or symlink).

            Detach the node after execution.
            """
            if ops[node.dst] == DLeafOp.UNLINK:
                self._unlink(node.dst)

            return detach_node(node)

        callbacks = Callbacks(branch=execute_branch, leaf=execute_leaf)
        walk_tree(tree, callbacks=callbacks, order=VisitOrder.POST)
        return tree

    def _rmdir(self, path: Path) -> None:
        if self.dry_run:
            return logger.info("Remove directory %s, no effect if it is not empty", path)

        if next(path.iterdir(), None) is None:
            path.rmdir()
            return logger.info("Removed empty directory %s", path)

        return logger.debug("Directory %s is not empty, skip removing it", path)

    def _unlink(self, path: Path) -> None:
        if self.dry_run:
            return logger.info("Unlink %s, no effect if it does not exist.", path)

        try:
            path.unlink()
        except FileNotFoundError:
            return logger.debug("File %s does not exist, skip unlinking it", path)
        else:
            return logger.info("Unlinked %s", path)
