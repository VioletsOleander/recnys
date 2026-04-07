from typing import TYPE_CHECKING

from recnys.backend.model import BranchNode, LeafNode, RootNode

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["walk_subtree", "walk_tree"]


def walk_tree(
    root: RootNode,
    on_branch: Callable[[BranchNode], BranchNode] | None = None,
    on_leaf: Callable[[LeafNode], BranchNode | LeafNode] | None = None,
    *,
    update: bool,
) -> RootNode:
    """Traverse the node tree rooted at `root` in depth-first order.

    The callback functions `on_branch`, and `on_leaf` will be called when visiting the respective
    types of nodes, before visiting their children.

    If `update` is `True`, the return value of callback functions (if the callback is not `None`) will be
    used to replace the visited node in the tree.

    Args:
        root (RootNode): The root node of the node tree to be traversed.
        on_branch (Callable[[BranchNode], BranchNode] | None): The callback function to be called
            when visiting a branch node.
        on_leaf (Callable[[LeafNode], BranchNode | LeafNode] | None): The callback function to be called
            when visiting a leaf node.
        update (bool): Whether to update the tree with the return values of callback functions.

    Returns:
        RootNode: The root node of the node tree after traversal.
    """
    for child in root.children.values():
        child_node = walk_subtree(child, on_branch, on_leaf, update=update)

        if not update:
            continue
        root.children[child.dst] = child_node

    return root


def walk_subtree(
    node: BranchNode | LeafNode,
    on_branch: Callable[[BranchNode], BranchNode] | None = None,
    on_leaf: Callable[[LeafNode], BranchNode | LeafNode] | None = None,
    *,
    update: bool,
) -> BranchNode | LeafNode:
    """Traverse a subtree rooted at `node`, calling callbacks when visiting nodes.

    If `update` is `True`, the return value of callback functions (if the callback is not `None`) will be
    used to replace the visited node in the tree.

    If the corresponding callback is `None`, the visited node will be returned as is. Otherwise, the return
    value of the callback on `node` will be returned.

    Args:
        node (BranchNode | LeafNode): The root node of the subtree to be traversed.
        on_branch (Callable[[BranchNode], BranchNode] | None): The callback function to be called
            when visiting a branch node.
        on_leaf (Callable[[LeafNode], BranchNode | LeafNode] | None): The callback function to be called
            when visiting a leaf node.
        update (bool): Whether to update the tree with the return values of callback functions.

    Returns:
        BranchNode | LeafNode: The input node as is or the return value of its callback function.
    """
    if isinstance(node, LeafNode):
        return on_leaf(node) if on_leaf is not None else node

    branch = on_branch(node) if on_branch is not None else node

    for child in node.children.values():
        child_node = walk_subtree(child, on_branch, on_leaf, update=update)

        if not update:
            continue
        node.children[child.dst] = child_node

    return branch
