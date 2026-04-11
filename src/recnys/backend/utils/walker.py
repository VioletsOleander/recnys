from enum import Enum, auto
from typing import TYPE_CHECKING, NamedTuple

from recnys.backend.model import BranchNode, LeafNode, Node, Tree

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Callbacks", "VisitOrder", "walk_tree"]


class VisitOrder(Enum):
    """The order to call the callback functions when traversing a node tree.

    Attributes:
        PRE: Pre-order, where the callback function is called before visiting the children of a node.
        POST: Post-order, where the callback function is called after visiting the children of a node.
    """

    PRE = auto()
    POST = auto()


class Callbacks(NamedTuple):
    """Callbacks to be called when visiting nodes during tree traversal.

    Attributes:
        branch: The function to be called when visiting a branch node, or `None`.
        leaf: The function to be called when visiting a leaf node, or `None`.
    """

    branch: Callable[[BranchNode], None] | None
    leaf: Callable[[LeafNode], None] | None


def walk_tree(tree: Tree, callbacks: Callbacks, order: VisitOrder) -> None:
    """Traverse the node tree in depth-first style.

    If not `None`, the callbacks will be called when visiting the respective types of nodes. For pre order
    traversal, the callback will be called before visiting the children, and vice versa.

    Args:
        tree (Tree): The node tree to be traversed.
        callbacks (Callbacks): The callbacks to be called when visiting nodes.
        order (VisitOrder): When to call the callback functions.
    """
    root = tree.root
    for child in root.children.values():
        _walk_subtree(child, callbacks=callbacks, order=order)


def _walk_subtree(node: Node, callbacks: Callbacks, order: VisitOrder) -> None:
    """Traverse a subtree rooted at `node`, calling callbacks when visiting nodes."""
    if isinstance(node, LeafNode):
        on_leaf = callbacks.leaf
        return on_leaf(node) if on_leaf is not None else None

    on_branch = callbacks.branch

    if order == VisitOrder.PRE and on_branch is not None:
        on_branch(node)

    for child in node.children.values():
        _walk_subtree(child, callbacks=callbacks, order=order)

    if order == VisitOrder.POST and on_branch is not None:
        on_branch(node)

    return None
