"""Provide `DTreeExecutor`."""

import logging
from typing import TYPE_CHECKING

from recnys.tree.model import BranchNode, DBranchOp, DLeafOp, DTree, LeafNode, Node
from recnys.tree.utils.collector import collect_nodes
from recnys.tree.utils.walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["DTreeExecutor"]

logger = logging.getLogger(__name__)


class DTreeExecutor:
    """DTreeExecutor executes a deletion tree.

    The main provided method is `execute`.

    Attributes:
        tree (DTree): The deletion tree instance constructed during the execution.
        num_executed_ops (int): The number of operations executed during the execution.
        dry_run (bool): Whether to perform a dry run of the execution.
    """

    tree: DTree
    num_executed_ops: int
    dry_run: bool

    def __init__(self, *, dry_run: bool) -> None:
        """Initialize the DTreeExecutor.

        Args:
            dry_run (bool): Whether to perform a dry run of the execution.
        """
        self.dry_run = dry_run
        self.num_executed_ops = 0

    def execute(self, dtree: DTree) -> DTree:
        """Execute the given dtree.

        Return a new dtree with the executed nodes detached from the tree. If all nodes are executed
        successfully, the returned dtree will be an root node with no children.

        Args:
            dtree (RootNode): The root node of the deletion tree to be executed.

        Returns:
            RootNode: The root node of the deletion tree with the executed nodes detached from the tree
        """
        logger.debug("Executing deletion tree.")

        self.tree = dtree.model_copy(deep=True)
        parents = collect_nodes(self.tree, collect_leaf=False)
        parents[self.tree.root.dst] = self.tree.root
        ops = self.tree.ops

        def detach_node(node: Node) -> None:
            parent = parents[node.dst.parent]
            parent.children.pop(node.dst)
            ops.pop(node.dst, None)

        def execute_branch(node: BranchNode) -> None:
            """Execute deletion op (remove) on branch node (dir).

            Detach the node after execution.
            """
            if ops.get(node.dst) == DBranchOp.REMOVE:
                self._rmdir(node.dst)

            return detach_node(node)

        def execute_leaf(node: LeafNode) -> None:
            """Execute deletion op (unlink) on leaf node (file or symlink).

            Detach the node after execution.
            """
            if ops.get(node.dst) == DLeafOp.UNLINK:
                self._unlink(node.dst)

            return detach_node(node)

        callbacks = Callbacks(branch=execute_branch, leaf=execute_leaf)
        walk_tree(dtree, callbacks=callbacks, order=VisitOrder.POST)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Executed deletion tree, remaining tree: %s", self.tree.model_dump_json(indent=2)
            )

        return self.tree

    def _rmdir(self, dst: Path) -> None:
        if not dst.exists():
            return logger.debug("Directory %s does not exist, skip removing it", dst)

        if not dst.is_dir(follow_symlinks=False):
            raise RuntimeError(
                f"Path {dst} is occupied, failed to remove the directory.\n"
                "Hint: Please remove the file or symbolic link at the path."
            )

        if next(dst.iterdir(), None) is not None:
            return logger.debug("Directory %s is not empty, skip removing it", dst)

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Remove"
        else:
            dst.rmdir()
            verb = "Removed"

        return logger.info("%s empty directory %s.", verb, dst)

    def _unlink(self, dst: Path) -> None:
        if not dst.exists(follow_symlinks=False):
            return logger.debug("File/Symlink %s does not exist, skip unlinking it", dst)

        if not dst.is_symlink() and not dst.is_file():
            raise RuntimeError(
                f"Path {dst} is occupied, failed to unlink the file or symbolic link.\n"
                "Hint: Please remove the directory at the path."
            )

        self.num_executed_ops += 1

        if self.dry_run:
            verb = "Unlink"
        else:
            dst.unlink()
            verb = "Unlinked"

        return logger.info("%s %s.", verb, dst)
