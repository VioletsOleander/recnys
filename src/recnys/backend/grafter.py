"""Provide TreeGrafter."""

from typing import TYPE_CHECKING, overload

from .model import BranchNode, LeafNode, Node, Operation, RootNode
from .utils.traversal import walk_tree

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

        @overload
        def add_node(node: BranchNode) -> BranchNode: ...

        @overload
        def add_node(node: LeafNode) -> LeafNode: ...

        def add_node(node: BranchNode | LeafNode) -> BranchNode | LeafNode:
            nodes[node.dst] = node
            return node

        walk_tree(root, on_branch=add_node, on_leaf=add_node, update=False)

        # Graft nodes that exist under prev_root but not under root
        def graft_branch(node: BranchNode) -> BranchNode:
            if node.dst in nodes:
                return node

            parent = nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            graft_node = BranchNode(dst=node.dst, op=Operation.REMOVE, children=node.children)
            parent.children[node.dst] = graft_node
            return graft_node

        def graft_leaf(node: LeafNode) -> LeafNode:
            if node.dst in nodes:
                return node

            parent = nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            op = Operation.UNLINK if node.op == Operation.LINK else Operation.REMOVE
            graft_node = LeafNode(src=node.src, dst=node.dst, op=op)
            parent.children[node.dst] = graft_node
            return node

        walk_tree(prev_root, on_branch=graft_branch, on_leaf=graft_leaf, update=False)

        return root
