from enum import Enum, auto
from typing import TYPE_CHECKING, TypedDict, cast, overload

from recnys.backend.ctree.model import CBranchNode, CLeafNode, CRootNode
from recnys.backend.dtree.model import DBranchNode, DLeafNode, DRootNode

if TYPE_CHECKING:
    from collections.abc import Callable

__all__ = ["Callbacks", "Order", "walk_subtree", "walk_tree"]

type RootNode = CRootNode | DRootNode
type Callbacks = CCallbacks | DCallbacks


class Order(Enum):
    """The order of traversal.

    Attributes:
        PRE: Pre-order, where the callback function is called before visiting the children of a node.
        POST: Post-order, where the callback function is called after visiting the children of a node.
    """

    PRE = auto()
    POST = auto()


class CCallbacks(TypedDict):
    """The callback functions for CTree traversal.

    Attributes:
        root: The callback function to be called when visiting a root node, `None` if no callback is needed.
            Signature: `Callable[[CRootNode], CRootNode]`
        branch: The callback function to be called when visiting a branch node, `None` if no callback is needed.
            Signature: `Callable[[CBranchNode], CBranchNode]`
        leaf: The callback function to be called when visiting a leaf node, `None` if no callback is needed.
            Signature: `Callable[[CLeafNode], CBranchNode | CLeafNode]`
    """

    root: Callable[[CRootNode], CRootNode] | None
    branch: Callable[[CBranchNode], CBranchNode] | None
    leaf: Callable[[CLeafNode], CBranchNode | CLeafNode] | None


class DCallbacks(TypedDict):
    """The callback functions for DTree traversal.

    Attributes:
        root: The callback function to be called when visiting a root node, `None` if no callback is needed.
            Signature: `Callable[[DRootNode], DRootNode]`
        branch: The callback function to be called when visiting a branch node, `None` if no callback is needed.
            Signature: `Callable[[DBranchNode], DBranchNode]`
        leaf: The callback function to be called when visiting a leaf node, `None` if no callback is needed.
            Signature: `Callable[[DLeafNode], DBranchNode | DLeafNode]`
    """

    root: Callable[[DRootNode], DRootNode] | None
    branch: Callable[[DBranchNode], DBranchNode] | None
    leaf: Callable[[DLeafNode], DBranchNode | DLeafNode] | None


@overload
def walk_tree(
    root: CRootNode, callbacks: CCallbacks, order: Order, *, update: bool
) -> CRootNode: ...


@overload
def walk_tree(
    root: DRootNode, callbacks: DCallbacks, order: Order, *, update: bool
) -> DRootNode: ...


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

    if order == Order.PRE and on_root is not None:
        root = on_root(root)  # type: ignore[invalid-argument-type]

    for dst, child in root.children.items():
        child_node = walk_subtree(child, callbacks, order=order, update=update)

        if update:
            root.children[dst] = child_node

    if order == Order.POST and on_root is not None:
        root = on_root(root)  # type: ignore[invalid-argument-type]

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

    if order == Order.PRE and on_branch is not None:
        node = on_branch(node)

    for dst, child in node.children.items():
        child_node = walk_subtree(child, callbacks, order=order, update=update)

        if update:
            node.children[dst] = child_node

    if order == Order.POST and on_branch is not None:
        node = on_branch(node)

    return node
