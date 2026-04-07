from typing import TYPE_CHECKING

from recnys.parsing.model import BranchNode, LeafNode, Operation, RootNode

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["TreeCanonicalizer"]


class TreeCanonicalizer:
    """TreeCanonicalizer canonicalizes the node tree.

    The main provided method is `canonicalize`.
    """

    def canonicalize(self, root: RootNode) -> RootNode:
        """Canonicalize the node tree rooted at `root`.

        The canonicalization process will branchify any leaf node
        that corresponds to a directory with COPY operation.

        Args:
            root (RootNode): The root node of the node tree to be canonicalized.

        Returns:
            RootNode: The root node of the canonicalized node tree.
        """
        for child in root.children.values():
            self._canonicalize_node(child)

        return root

    def _canonicalize_node(self, node: BranchNode | LeafNode) -> None:
        """Canonicalize a node in the node tree.

        The canonicalization process includes:

        - For a branch node, recursively canonicalize its child nodes.
        - For a leaf node that corresponds to a directory with COPY operation, branchify it.
        """
        if isinstance(node, BranchNode):
            for child in node.children.values():
                self._canonicalize_node(child)
            return

        if node.src.is_dir() and node.op == Operation.COPY:
            self._branchify_leaf(node, exclude_dirs=[".git"])

    def _branchify_leaf(self, leaf: LeafNode, exclude_dirs: list[str]) -> None:
        """Transform a leaf node into branch node.

        The leaf node should be a directory with COPY operation.

        All files under the directory and its subdirectories (excluding those specified in
        `exclude_dirs`) will be expanded into leaf nodes.
        """
        if not leaf.src.is_dir():
            raise ValueError("The leaf node to branchify must correspond to a directory.")
        if leaf.op != Operation.COPY:
            raise ValueError("The leaf node to branchify must have COPY operation.")

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
