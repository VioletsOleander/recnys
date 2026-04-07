"""Provide TreeGrafter."""

from typing import TYPE_CHECKING

from .model import BranchNode, LeafNode, Node, Operation, RootNode
from .utils import walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["TreeGrafter"]


class TreeGrafter:
    """TreeGrafter grafts deleted nodes from the previous node tree into the current node tree.

    The main provided method is `graft`.
    """

    def graft(self, root: RootNode, prev_root: RootNode) -> RootNode:
        """Graft deleted nodes from `prev_root` into `root`.

        The grafting process will add nodes that exist under `prev_root` but not under `root` into `root` with
        REMOVE or UNLINK operation.

        Args:
            root (RootNode): The root node of the node tree to be grafted.
            prev_root (RootNode): The root node of the previous node tree, which is used as reference for
                grafting.

        Returns:
            RootNode: The root node of the grafted node tree, which is the same as `root` but with additional
                nodes grafted.
        """
        # Store nodes under root

        nodes: dict[Path, Node] = {}

        def add_node(node: BranchNode | LeafNode) -> None:
            nodes[node.dst] = node

        walk_tree(root, on_branch=add_node, on_leaf=add_node)

        # Graft nodes that exist under prev_root but not under root

        def graft_branch(node: BranchNode) -> None:
            if node.dst in nodes:
                return

            parent = nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            graft_node = BranchNode(dst=node.dst, op=Operation.REMOVE, parent=parent)
            parent.children[node.dst] = graft_node

        def graft_leaf(node: LeafNode) -> None:
            if node.dst in nodes:
                return

            parent = nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            op = Operation.UNLINK if node.op == Operation.LINK else Operation.REMOVE
            graft_node = LeafNode(src=node.src, dst=node.dst, op=op, parent=parent)
            parent.children[node.dst] = graft_node

        walk_tree(prev_root, on_branch=graft_branch, on_leaf=graft_leaf)

        return root
