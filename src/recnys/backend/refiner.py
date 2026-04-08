"""Provide `TreeRefiner`."""

from typing import TYPE_CHECKING

from .model import BranchNode, LeafNode, Operation, RootNode
from .utils.exception import handle_fnf
from .utils.traversal import walk_tree

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["TreeRefiner"]


class TreeRefiner:
    """TreeRefiner refines the parsed node tree.

    This stage can be analogized to the canonicalization stage in a compilation pipeline.

    The main provided method is `refine`.
    """

    def refine(self, root: RootNode) -> RootNode:
        """Refine the node tree rooted at `root`.

        The refinement process will branchify any leaf node that corresponds to a directory with
        COPY operation. For other nodes, no refinement is needed.

        Args:
            root (RootNode): The root node of the node tree to be refined.

        Returns:
            RootNode: The root node of the refined node tree.
        """

        @handle_fnf
        def refine_leaf(node: LeafNode) -> LeafNode | BranchNode:
            if not node.src.is_dir() or node.op != Operation.COPY:
                return node
            return self._branchify_leaf(node, exclude_dirs=[".git"])

        return walk_tree(root, on_leaf=refine_leaf, update=True)

    def _branchify_leaf(self, leaf: LeafNode, exclude_dirs: list[str]) -> BranchNode:
        """Transform a leaf node into branch node and return it.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
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
                node = LeafNode(src=leaf_src, dst=leaf_dst, op=Operation.COPY)
                parent.children[leaf_dst] = node

        return branch
