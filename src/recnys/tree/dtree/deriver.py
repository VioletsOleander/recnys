"""Provide `DTreeDeriver`."""

import logging
from typing import TYPE_CHECKING

from recnys.tree.model import BranchNode, CTree, DBranchOp, DLeafOp, DTree, LeafNode
from recnys.tree.utils.collector import collect_nodes
from recnys.tree.utils.walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["DTreeDeriver"]

logger = logging.getLogger(__name__)


class DTreeDeriver:
    """DTreeDeriver derives a deletion tree from the current creation tree and the previous creation tree.

    The main provided method is `derive`.
    """

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
        logger.debug("Deriving deletion tree from current and previous creation trees.")

        ops: dict[Path, DBranchOp | DLeafOp] = {}
        cnodes = collect_nodes(ctree)

        def derive_branch(node: BranchNode) -> None:
            """Turn deleted nodes to remove op."""
            if isinstance(cnodes.get(node.dst), BranchNode):
                return
            ops[node.dst] = DBranchOp.REMOVE

        def derive_leaf(node: LeafNode) -> None:
            """Turn deleted/op-changed nodes to unlink op."""
            if cnodes.get(node.dst) == node and ctree.ops.get(node.dst) == prev_ctree.ops[node.dst]:
                return
            ops[node.dst] = DLeafOp.UNLINK

        callbacks = Callbacks(branch=derive_branch, leaf=derive_leaf)
        walk_tree(prev_ctree, callbacks=callbacks, order=VisitOrder.PRE)

        dtree = DTree(root=prev_ctree.root, ops=ops)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("Derived deletion tree: %s", dtree.model_dump_json(indent=2))

        return dtree
