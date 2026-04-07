"""Provide `TreeRefiner`."""

from typing import TYPE_CHECKING

from .model import BranchNode, LeafNode, Operation, RootNode
from .utils import walk_tree

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

        def refine_leaf(node: LeafNode) -> None:
            if not node.src.is_dir() or node.op != Operation.COPY:
                return
            self._branchify_leaf(node, exclude_dirs=[".git"])

        walk_tree(root, on_leaf=refine_leaf)
        return root

    def _branchify_leaf(self, leaf: LeafNode, exclude_dirs: list[str]) -> None:
        """Transform a leaf node into branch node.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
        src = leaf.src
        dst = leaf.dst
        branch = BranchNode(dst=dst, parent=leaf.parent)

        parent = branch.parent
        parent.children[dst] = branch
        parents: dict[Path, BranchNode | RootNode] = {
            parent.dst: parent,
            branch.dst: branch,
        }

        for dir_path, dir_names, file_names in src.walk(top_down=True):  # DFS
            for name in exclude_dirs:
                if name in dir_names:
                    dir_names.remove(name)

            branch_dst = dst / dir_path.relative_to(src)
            if branch_dst in parents:
                parent = parents[branch_dst]
            else:
                node = BranchNode(dst=branch_dst, parent=parent)
                parents[branch_dst] = node
                parent = node

            for file_name in file_names:
                leaf_src = dir_path / file_name
                leaf_dst = dst / leaf_src.relative_to(src)
                node = LeafNode(src=leaf_src, dst=leaf_dst, op=Operation.COPY, parent=parent)
                parent.children[leaf_dst] = node
