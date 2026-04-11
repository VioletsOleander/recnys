"""Provide `DTreeExecutor`."""

import logging
from typing import TYPE_CHECKING, overload

from recnys.backend.model import DTree
from recnys.backend.utils.collector import collect_nodes
from recnys.backend.utils.walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["DTreeExecutor"]


class DTreeExecutor:
    """DTreeExecutor executes a deletion tree.

    The main provided method is `execute`.

    Attributes:
        dtree (RootNode): The root node of the deletion tree after execution.
        dry_run (bool): Whether to perform a dry run of the execution.
            If True, the execution will only log the operations without actually performing them.
    """

    dtree: RootNode
    dry_run: bool
    _parent_nodes: dict[Path, RootNode | BranchNode]

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
        self.dtree = dtree.model_copy(deep=True)
        self._parent_nodes = collect_nodes(self.dtree, collect_leaf=False)

        callbacks = Callbacks(root=None, branch=self._execute_branch, leaf=self._execute_leaf)
        walk_tree(dtree, callbacks=callbacks, order=VisitOrder.POST, update=False)
        return dtree

    def _execute_branch(self, node: BranchNode) -> BranchNode:
        """Execute deletion op (nop or remove) on branch node (dir).

        Detach the executed node from self.dtree and return it.
        """
        if node.op == Operation.NOP:
            return self._detach_node(node)

        if self.dry_run:
            logger.info("Remove %s, no effect if it is not empty", node.dst)

        if next(node.dst.iterdir(), None) is None:
            node.dst.rmdir()
            logger.info("Removed %s", node.dst)

        return self._detach_node(node)

    def _execute_leaf(self, node: LeafNode) -> LeafNode:
        """Execute deletion op (nop or unlink) on leaf node (file or symlink).

        Detach the executed node from self.dtree and return it.
        """
        if node.op == Operation.NOP:
            return self._detach_node(node)

        if self.dry_run:
            logger.info("Unlink %s, no effect if it does not exist.", node.dst)
            return self._detach_node(node)

        node.dst.unlink(missing_ok=True)
        logger.info("Unlinked %s", node.dst)

        return self._detach_node(node)

    @overload
    def _detach_node(self, node: BranchNode) -> BranchNode: ...

    @overload
    def _detach_node(self, node: LeafNode) -> LeafNode: ...

    def _detach_node(self, node: BranchNode | LeafNode) -> BranchNode | LeafNode:
        parent = self._parent_nodes[node.dst.parent]
        return parent.children.pop(node.dst)
