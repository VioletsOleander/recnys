"""Provide `DTreeDeriver`."""

from typing import TYPE_CHECKING, overload

from recnys.backend.model import BranchNode, LeafNode, Operation, RootNode
from recnys.backend.utils.traversal import Callbacks, Order, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["DTreeDeriver"]


class DTreeDeriver:
    def derive(self, root: RootNode, prev_root: RootNode) -> RootNode:
        """Derive a deletion tree from creation tree `root` and `prev_root`.

        The deletion tree aims to resolve the deletion operations brought by:

        - Deleted nodes, whose node.dst was created by last execution, but does not exist in the expected
            result of current execution.
        - Changed nodes, whose node.dst was created by last execution, but its existence form is changed in
            the expected result of current execution.

        Args:
            root (RootNode): The root node of the creation tree.
            prev_root (RootNode): The root node of the previous creation tree.

        Returns:
            RootNode: The root node of the derived deletion tree.
        """
        curr_nodes = self._collect_nodes(root)

        def derive_branch(node: BranchNode) -> BranchNode:
            """Turn kept nodes to no op, deleted nodes to remove op."""
            if node == curr_nodes.get(node.dst):
                return BranchNode(dst=node.dst, op=Operation.NOP, children=node.children)

            return BranchNode(dst=node.dst, op=Operation.REMOVE, children=node.children)

        def derive_leaf(node: LeafNode) -> LeafNode:
            """Turn kept nodes to no op, deleted nodes to unlink/remove op."""
            if node == curr_nodes.get(node.dst):
                return LeafNode(src=node.src, dst=node.dst, op=Operation.NOP)

            op = Operation.UNLINK if node.op == Operation.LINK else Operation.REMOVE
            return LeafNode(src=node.src, dst=node.dst, op=op)

        callbacks = Callbacks(root=None, branch=derive_branch, leaf=derive_leaf)
        walk_tree(prev_root, callbacks=callbacks, order=Order.PRE, update=True)

        return prev_root

    def _collect_nodes(self, root: RootNode) -> dict[Path, BranchNode | LeafNode]:
        """Collect all nodes under `root` into a dictionary and return it.

        Dict keys are `node.dst`, values are the corresponding nodes.
        """
        nodes: dict[Path, BranchNode | LeafNode] = {}

        @overload
        def add_node(node: BranchNode) -> BranchNode: ...

        @overload
        def add_node(node: LeafNode) -> LeafNode: ...

        def add_node(node: BranchNode | LeafNode) -> BranchNode | LeafNode:
            nodes[node.dst] = node
            return node

        callbacks = Callbacks(root=None, branch=add_node, leaf=add_node)
        walk_tree(root, callbacks=callbacks, order=Order.PRE, update=False)

        return nodes
