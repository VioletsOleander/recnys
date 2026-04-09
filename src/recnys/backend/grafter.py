"""Provide TreeGrafter."""

from typing import TYPE_CHECKING, overload

from .model import BranchNode, LeafNode, Node, Operation, RootNode
from .utils.traversal import Callbacks, Order, walk_tree

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
        curr_nodes = self._collect_nodes(root)

        # Graft nodes that exist under prev_root but not under root
        # Two possible cases for such nodes:
        # - creation related node, created in last execution
        # - deletion related node, not finished by last execution
        def graft_branch(node: BranchNode) -> BranchNode:
            if node.dst in curr_nodes:
                return node

            parent = curr_nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            graft_node = BranchNode(dst=node.dst, op=Operation.REMOVE, children=node.children)
            parent.children[node.dst] = graft_node
            return graft_node

        def graft_leaf(node: LeafNode) -> LeafNode:
            if node.dst in curr_nodes:
                return node

            parent = curr_nodes[node.dst.parent]
            if isinstance(parent, LeafNode):
                raise TypeError("Incorrect tree structure, leaf node can not be parent.")

            op = node.op
            if op not in (Operation.REMOVE, Operation.UNLINK):
                op = Operation.UNLINK if op == Operation.LINK else Operation.REMOVE

            graft_node = LeafNode(src=node.src, dst=node.dst, op=op)
            parent.children[node.dst] = graft_node
            return node

        callbacks = Callbacks(root=None, branch=graft_branch, leaf=graft_leaf)
        walk_tree(prev_root, callbacks=callbacks, order=Order.PRE, update=False)

        return root

    def _collect_nodes(self, root: RootNode) -> dict[Path, Node]:
        """Collect all nodes under `root` into a dictionary and return it.

        Dict keys are `node.dst`, values are the corresponding nodes.
        """
        nodes: dict[Path, Node] = {root.dst: root}

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
