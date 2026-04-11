"""Provide `CTreeExpander`."""

from typing import TYPE_CHECKING

from recnys.backend.model import BranchNode, BranchOp, CBranchOp, CLeafOp, CTree, LeafNode, LeafOp
from recnys.backend.utils.walker import Callbacks, walk_tree

from .utils import handle_fnf

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["CTreeExpander"]


class CTreeExpander:
    """CTreeExpander expands the parsed creation tree.

    The main provided method is `expand`.
    """

    _ops: dict[Path, CBranchOp | CLeafOp]

    def expand(self, ctree: CTree) -> CTree:
        """Expand the creation tree.

        The expansion process will branchify any leaf node that corresponds to a directory with
        COPY operation. For other nodes, no expansion is needed.

        Args:
            ctree (CTree): The creation tree to be expanded.

        Returns:
            CTree: The expanded creation tree.
        """
        self._ops = ctree.ops

        @handle_fnf
        def expand_leaf(node: LeafNode) -> None:
            if not node.src.is_dir() or node.op != LeafOp.COPY:
                return node
            return self._branchify_leaf(node, exclude_dirs=[".git"])

        callbacks = Callbacks(root=None, branch=None, leaf=expand_leaf)

        walk_tree(ctree, callbacks=callbacks, order=VisitOrder.PRE)

        return tree

    def _branchify_leaf(self, leaf: LeafNode, exclude_dirs: list[str]) -> BranchNode:
        """Transform a leaf node into branch node and return it.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
        src = leaf.src
        dst = leaf.dst
        branch = BranchNode(dst=dst, op=BranchOp.CREATE)

        parents: dict[Path, BranchNode] = {branch.dst: branch}

        for dir_path, dir_names, file_names in src.walk(top_down=True):  # DFS
            for name in exclude_dirs:
                if name in dir_names:
                    dir_names.remove(name)

            branch_dst = dst / dir_path.relative_to(src)
            if branch_dst in parents:
                parent = parents[branch_dst]
            else:
                node = BranchNode(dst=branch_dst, op=BranchOp.CREATE)
                parents[branch_dst] = node
                parent.children[branch_dst] = node
                parent = node

            for file_name in file_names:
                leaf_src = dir_path / file_name
                leaf_dst = dst / leaf_src.relative_to(src)
                node = LeafNode(src=leaf_src, dst=leaf_dst, op=LeafOp.COPY)
                parent.children[leaf_dst] = node

        return branch
