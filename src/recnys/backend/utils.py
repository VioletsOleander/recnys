from typing import TYPE_CHECKING

from .model import BranchNode, LeafNode, RootNode

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["walk_tree"]


def walk_tree(
    root: RootNode,
    on_root: Callable[[RootNode], None] | None = None,
    on_branch: Callable[[BranchNode], None] | None = None,
    on_leaf: Callable[[LeafNode], None] | None = None,
) -> None:
    """Traverse the node tree rooted at `root`.

    The callback functions `on_root`, `on_branch`, and `on_leaf` will be called when visiting the respective
    types of nodes.

    The traversal order is pre-order.

    Args:
        root (RootNode): The root node of the node tree to be traversed.
        on_root (Callable[[RootNode], None] | None): The callback function to be called when visiting the root node.
        on_branch (Callable[[BranchNode], None] | None): The callback function to be called when visiting a branch node.
        on_leaf (Callable[[LeafNode], None] | None): The callback function to be called when visiting a leaf node.
    """
    if on_root is not None:
        on_root(root)

    for child in root.children.values():
        _walk_subtree(child, on_branch=on_branch, on_leaf=on_leaf)


def _walk_subtree(
    node: BranchNode | LeafNode,
    on_branch: Callable[[BranchNode], None] | None = None,
    on_leaf: Callable[[LeafNode], None] | None = None,
) -> None:
    """Traverse a subtree rooted at `node`."""
    if isinstance(node, LeafNode):
        if on_leaf is not None:
            on_leaf(node)
        return

    if on_branch is not None:
        on_branch(node)

    for child in node.children.values():
        _walk_subtree(child, on_branch=on_branch, on_leaf=on_leaf)
