from enum import Enum, auto
from typing import TYPE_CHECKING, TypedDict

from recnys.backend.model import BranchNode, LeafNode, RootNode

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Callbacks", "Order", "walk_subtree", "walk_tree"]


class Order(Enum):
    """The order of traversal.

    Attributes:
        PRE: Pre-order, where the callback function is called before visiting the children of a node.
        POST: Post-order, where the callback function is called after visiting the children of a node.
    """

    PRE = auto()
    POST = auto()


class Callbacks(TypedDict):
    """The callback functions for each node type.

    Attributes:
        root: The callback function to be called when visiting a root node, `None` if no callback is needed.
            Signature: `Callable[[RootNode], RootNode]`
        branch: The callback function to be called when visiting a branch node, `None` if no callback is needed.
            Signature: `Callable[[BranchNode], BranchNode]`
        leaf: The callback function to be called when visiting a leaf node, `None` if no callback is needed.
            Signature: `Callable[[LeafNode], BranchNode | LeafNode]`
    """

    root: Callable[[RootNode], RootNode] | None
    branch: Callable[[BranchNode], BranchNode] | None
    leaf: Callable[[LeafNode], BranchNode | LeafNode] | None


def walk_tree(root: RootNode, callbacks: Callbacks, order: Order, *, update: bool) -> RootNode:
    """Traverse the node tree rooted at `root` in depth-first style.

    If not `None`, the callback functions `root`, `branch`, `leaf` will be called when visiting the
    respective types of nodes, furthermore, if `update` is `True`, their return value will be used to replace
    the visited types of nodes.

    For pre order traversal, the callback will be called before visiting the children, and vice versa.

    Args:
        root (RootNode): The root node of the node tree to be traversed.
        callbacks (Callbacks): The callback functions for each node type.
        order (Order): When to call the callback functions.
        update (bool): Whether to update the tree with the return values of callback functions.

    Returns:
        RootNode: The root node of the node tree after traversal.
    """
    on_root = callbacks["root"]

    if order == Order.PRE:
        root = on_root(root) if on_root is not None else root

    for child in root.children.values():
        child_node = walk_subtree(child, callbacks, order=order, update=update)

        if not update:
            continue
        root.children[child.dst] = child_node

    if order == Order.POST:
        root = on_root(root) if on_root is not None else root

    return root


def walk_subtree(
    node: BranchNode | LeafNode, callbacks: Callbacks, order: Order, *, update: bool
) -> BranchNode | LeafNode:
    """Traverse a subtree rooted at `node`, calling callbacks when visiting nodes.

    If not `None`, the callback functions `branch`, `leaf` will be called when visiting the respective
    types of nodes, furthermore, if `update` is `True`, their return value will be used to replace the visited
    types of nodes.

    For pre order traversal, the callback will be called before visiting the children, and vice versa.

    Args:
        node (BranchNode | LeafNode): The root node of the subtree to be traversed.
        callbacks (Callbacks): The callback functions for each node type.
        order (Order): When to call the callback functions.
        update (bool): Whether to update the tree with the return values of callback functions.

    Returns:
        BranchNode | LeafNode: The input node as is or the return value of its callback function.
    """
    if isinstance(node, LeafNode):
        on_leaf = callbacks["leaf"]
        return on_leaf(node) if on_leaf is not None else node

    on_branch = callbacks["branch"]

    if order == Order.PRE:
        node = on_branch(node) if on_branch is not None else node

    for child in node.children.values():
        child_node = walk_subtree(child, callbacks, order=order, update=update)

        if not update:
            continue
        node.children[child.dst] = child_node

    if order == Order.POST:
        node = on_branch(node) if on_branch is not None else node

    return node
