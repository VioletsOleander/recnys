"""Provide `CTreeExpander`."""

from typing import TYPE_CHECKING

from recnys.backend.utils.exception import handle_fnf
from recnys.backend.utils.traversal import Callbacks, Order, walk_tree

from .model import CBranchNode, CBranchOp, CLeafNode, CLeafOp, CRootNode

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["CTreeExpander"]


class CTreeExpander:
    """CTreeExpander expands the parsed creation tree.

    The main provided method is `expand`.
    """

    def expand(self, ctree: CRootNode) -> CRootNode:
        """Expand the creation tree.

        The expansion process will branchify any leaf node that corresponds to a directory with
        COPY operation. For other nodes, no expansion is needed.

        Args:
            ctree (CRootNode): The root node of the creation tree to be expanded.

        Returns:
            CRootNode: The root node of the expanded creation tree.
        """

        @handle_fnf
        def expand_leaf(node: CLeafNode) -> CLeafNode | CBranchNode:
            if not node.src.is_dir() or node.op != CLeafOp.COPY:
                return node
            return self._branchify_leaf(node, exclude_dirs=[".git"])

        callbacks = Callbacks(root=None, branch=None, leaf=expand_leaf)

        return walk_tree(ctree, callbacks=callbacks, order=Order.PRE)

    def _branchify_leaf(self, leaf: CLeafNode, exclude_dirs: list[str]) -> CBranchNode:
        """Transform a leaf node into branch node and return it.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
        src = leaf.src
        dst = leaf.dst
        branch = CBranchNode(dst=dst, op=CBranchOp.CREATE)

        parents: dict[Path, CBranchNode] = {branch.dst: branch}

        for dir_path, dir_names, file_names in src.walk(top_down=True):  # DFS
            for name in exclude_dirs:
                if name in dir_names:
                    dir_names.remove(name)

            branch_dst = dst / dir_path.relative_to(src)
            if branch_dst in parents:
                parent = parents[branch_dst]
            else:
                node = CBranchNode(dst=branch_dst, op=CBranchOp.CREATE)
                parents[branch_dst] = node
                parent.children[branch_dst] = node
                parent = node

            for file_name in file_names:
                leaf_src = dir_path / file_name
                leaf_dst = dst / leaf_src.relative_to(src)
                node = CLeafNode(src=leaf_src, dst=leaf_dst, op=CLeafOp.COPY)
                parent.children[leaf_dst] = node

        return branch
