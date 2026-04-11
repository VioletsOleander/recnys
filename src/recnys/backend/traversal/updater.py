# ruff: noqa: UP046, UP047, Reusable typevar is needed here

from enum import Enum, auto
from typing import TYPE_CHECKING, Generic, TypedDict, TypeVar

from recnys.backend.ctree.model import CBranchNode, CLeafNode, CRootNode
from recnys.backend.dtree.model import DBranchNode, DLeafNode, DRootNode

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Callbacks", "Order", "update_subtree", "update_tree"]

R = TypeVar("R", CRootNode, DRootNode)
B = TypeVar("B", CBranchNode, DBranchNode)
L = TypeVar("L", CLeafNode, DLeafNode)


class Order(Enum):
    """The order of traversal.

    Attributes:
        PRE: Pre-order, where the callback function is called before visiting the children of a node.
        POST: Post-order, where the callback function is called after visiting the children of a node.
    """

    PRE = auto()
    POST = auto()


class Callbacks(TypedDict, Generic[R, B, L]):
    """The callback functions for each node type.

    Attributes:
        root: The callback function to be called when visiting a root node, `None` if no callback is needed.
            Signature: `Callable[[R], R]`
        branch: The callback function to be called when visiting a branch node, `None` if no callback is needed.
            Signature: `Callable[[B], B]`
        leaf: The callback function to be called when visiting a leaf node, `None` if no callback is needed.
            Signature: `Callable[[L], B | L]`
    """

    root: Callable[[R], R] | None
    branch: Callable[[B], B] | None
    leaf: Callable[[L], B | L] | None


def update_tree(root: R, callbacks: Callbacks[R, B, L], order: Order) -> R:
    """Traverse the node tree rooted at `root` in depth-first style.

    If not `None`, the callback functions `root`, `branch`, `leaf` will be called when visiting the
    respective types of nodes, furthermore, if `update` is `True`, their return value will be used to replace
    the visited types of nodes.

    For pre order traversal, the callback will be called before visiting the children, and vice versa.

    Args:
        root (RootNode): The root node of the node tree to be traversed.
        callbacks (Callbacks): The callback functions for each node type.
        order (Order): When to call the callback functions.

    Returns:
        RootNode: The root node of the node tree after traversal.
    """
    on_root = callbacks["root"]

    if order == Order.PRE and on_root is not None:
        root = on_root(root)

    for dst, child in root.children.items():
        root.children[dst] = update_subtree(
            child, callbacks["branch"], callbacks["leaf"], order=order
        )

    if order == Order.POST and on_root is not None:
        root = on_root(root)

    return root


def update_subtree(
    node: B | L,
    on_branch: Callable[[B], B] | None,
    on_leaf: Callable[[L], B | L] | None,
    order: Order,
) -> B | L:
    """Traverse a subtree rooted at `node`, calling callbacks when visiting nodes.

    If not `None`, the callback functions `branch`, `leaf` will be called when visiting the respective
    types of nodes, furthermore, if `update` is `True`, their return value will be used to replace the visited
    types of nodes.

    For pre order traversal, the callback will be called before visiting the children, and vice versa.

    Args:
        node (B | L): The root node of the subtree to be traversed.
        on_branch (Callable[[B], B] | None): The callback function to be called when visiting a branch node,
            `None` if no callback is needed.
        on_leaf (Callable[[L], B | L] | None): The callback function to be called when visiting a leaf node,
            `None` if no callback is needed.
        order (Order): When to call the callback functions.

    Returns:
        B | L: The input node as is or the return value of its callback function.
    """
    if isinstance(node, L.evaluate_constraints()):
        return on_leaf(node) if on_leaf is not None else node

    if order == Order.PRE and on_branch is not None:
        node = on_branch(node)

    for dst, child in node.children.items():
        node.children[dst] = update_subtree(child, on_branch, on_leaf, order=order)

    if order == Order.POST and on_branch is not None:
        node = on_branch(node)

    return node
