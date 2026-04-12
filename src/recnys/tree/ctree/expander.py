"""Provide `CTreeExpander`."""

import logging
from typing import TYPE_CHECKING

from recnys.tree.model import BranchNode, CLeafOp, CTree, LeafNode
from recnys.tree.utils.collector import collect_nodes
from recnys.tree.utils.walker import Callbacks, VisitOrder, walk_tree

from .utils import handle_fnf

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["CTreeExpander"]

logger = logging.getLogger(__name__)


class CTreeExpander:
    """CTreeExpander expands the parsed creation tree.

    The main provided method is `expand`.
    """

    _tree: CTree

    def expand(self, ctree: CTree) -> CTree:
        """Expand the creation tree.

        The expansion process will branchify any leaf node that corresponds to a directory with
        COPY operation. For other nodes, no expansion is needed.

        Args:
            ctree (CTree): The creation tree to be expanded.

        Returns:
            CTree: The expanded creation tree.
        """
        logger.debug("Expanding creation tree.")

        self._tree = ctree
        parents = collect_nodes(ctree, collect_leaf=False)
        parents[ctree.root.dst] = ctree.root

        @handle_fnf
        def expand_leaf(node: LeafNode) -> None:
            if node.src.is_dir() and ctree.ops[node.dst] == CLeafOp.COPY:
                branch = self._branchify_leaf(node, exclude_dirs=[".git"])
                parent = parents[node.dst.parent]
                parent.children[node.dst] = branch

        callbacks = Callbacks(branch=None, leaf=expand_leaf)
        walk_tree(ctree, callbacks=callbacks, order=VisitOrder.PRE)

        logger.debug("Expanded creation tree to: %s", self._tree)
        return self._tree

    def _branchify_leaf(self, leaf: LeafNode, exclude_dirs: list[str]) -> BranchNode:
        """Transform a leaf node into branch node and return it.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
        ops = self._tree.ops

        src = leaf.src
        dst = leaf.dst
        branch = BranchNode(dst=dst)

        parents: dict[Path, BranchNode] = {branch.dst: branch}

        for dir_path, dir_names, file_names in src.walk(top_down=True):  # DFS
            for name in exclude_dirs:
                if name in dir_names:
                    dir_names.remove(name)

            branch_dst = dst / dir_path.relative_to(src)
            if branch_dst in parents:
                parent = parents[branch_dst]
            else:
                node = BranchNode(dst=branch_dst)
                parents[branch_dst] = node
                parent.children[branch_dst] = node
                parent = node

            for file_name in file_names:
                leaf_src = dir_path / file_name
                leaf_dst = dst / leaf_src.relative_to(src)

                parent.children[leaf_dst] = LeafNode(src=leaf_src, dst=leaf_dst)
                ops[leaf_dst] = CLeafOp.COPY

        return branch
