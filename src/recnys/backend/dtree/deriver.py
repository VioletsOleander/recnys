"""Provide `DTreeDeriver`."""

from recnys.backend.model import BranchNode, LeafNode, Operation, RootNode
from recnys.backend.utils.collector import collect_nodes
from recnys.backend.utils.traversal import Callbacks, Order, walk_tree

__all__ = ["DTreeDeriver"]


class DTreeDeriver:
    """DTreeDeriver derives a deletion tree from the current creation tree and the previous creation tree.

    The main provided method is `derive`.
    """

    def derive(self, ctree: RootNode, prev_ctree: RootNode) -> RootNode:
        """Derive a deletion tree from `ctree` and `prev_ctree`.

        The deletion tree aims to resolve the deletion operations brought by:

        - Deleted nodes, whose node.dst was created by last execution, but does not exist in the expected
            result of current execution.
        - Changed nodes, whose node.dst was created by last execution, but its existence form is changed in
            the expected result of current execution.

        Args:
            ctree (RootNode): The root node of the current creation tree.
            prev_ctree (RootNode): The root node of the previous creation tree.

        Returns:
            RootNode: The root node of the derived deletion tree.
        """
        curr_nodes = collect_nodes(ctree, collect_root=False)

        def derive_branch(node: BranchNode) -> BranchNode:
            """Turn kept nodes to no op, deleted nodes to remove op."""
            if node == curr_nodes.get(node.dst):
                return BranchNode(dst=node.dst, op=Operation.NOP, children=node.children)

            return BranchNode(dst=node.dst, op=Operation.REMOVE, children=node.children)

        def derive_leaf(node: LeafNode) -> LeafNode:
            """Turn kept nodes to no op, deleted nodes to unlink op."""
            if node == curr_nodes.get(node.dst):
                return LeafNode(src=node.src, dst=node.dst, op=Operation.NOP)

            return LeafNode(src=node.src, dst=node.dst, op=Operation.UNLINK)

        callbacks = Callbacks(root=None, branch=derive_branch, leaf=derive_leaf)
        walk_tree(prev_ctree, callbacks=callbacks, order=Order.PRE, update=True)

        return prev_ctree
