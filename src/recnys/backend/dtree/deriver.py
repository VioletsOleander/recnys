"""Provide `DTreeDeriver`."""

from recnys.backend.model import CTree, DTree
from recnys.backend.utils.collector import collect_nodes
from recnys.backend.utils.walker import Callbacks, VisitOrder, walk_tree

__all__ = ["DTreeDeriver"]


class DTreeDeriver:
    """DTreeDeriver derives a deletion tree from the current creation tree and the previous creation tree.

    The main provided method is `derive`.
    """

    dtree: DTree

    def derive(self, ctree: CTree, prev_ctree: CTree) -> DTree:
        """Derive a deletion tree from `ctree` and `prev_ctree`.

        The deletion tree aims to resolve the deletion operations brought by:

        - Deleted nodes, whose node.dst was created by last execution, but does not exist in the expected
            result of current execution.
        - Changed nodes, whose node.dst was created by last execution, but its existence form is changed in
            the expected result of current execution.

        Args:
            ctree (CTree): The root node of the current creation tree.
            prev_ctree (CTree): The root node of the previous creation tree.

        Returns:
            DTree: The root node of the derived deletion tree.
        """
        self.dtree = DRootNode(dst=prev_ctree.dst)
        cnodes = collect_nodes(ctree)

        def derive_branch(node: DBranchNode) -> DBranchNode:
            """Turn kept nodes to no op, deleted nodes to remove op."""
            if node == cnodes.get(node.dst):
                return DBranchNode(dst=node.dst, op=Operation.NOP, children=node.children)

            return DBranchNode(dst=node.dst, op=Operation.REMOVE, children=node.children)

        def derive_leaf(node: DLeafNode) -> DLeafNode:
            """Turn kept nodes to no op, deleted nodes to unlink op."""
            if node == cnodes.get(node.dst):
                return DLeafNode(src=node.src, dst=node.dst, op=Operation.NOP)

            return DLeafNode(src=node.src, dst=node.dst, op=Operation.UNLINK)

        callbacks = Callbacks(root=None, branch=derive_branch, leaf=derive_leaf)
        walk_tree(prev_ctree, callbacks=callbacks, order=VisitOrder.PRE, update=True)

        return self.dtree
