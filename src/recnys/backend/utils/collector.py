from typing import TYPE_CHECKING, Literal, overload

from .traversal import Callbacks, Order, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.backend.model import BranchNode, LeafNode, Node, RootNode

__all__ = ["collect_nodes"]


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[True] = True,
    collect_branch: Literal[False],
    collect_leaf: Literal[False],
) -> dict[Path, RootNode]: ...


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[False],
    collect_branch: Literal[True] = True,
    collect_leaf: Literal[True] = True,
) -> dict[Path, BranchNode | LeafNode]: ...


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[False],
    collect_branch: Literal[False],
    collect_leaf: Literal[True] = True,
) -> dict[Path, LeafNode]: ...


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[True] = True,
    collect_branch: Literal[True] = True,
    collect_leaf: Literal[False],
) -> dict[Path, RootNode | BranchNode]: ...


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[False],
    collect_branch: Literal[True] = True,
    collect_leaf: Literal[True] = True,
) -> dict[Path, BranchNode | LeafNode]: ...


@overload
def collect_nodes(
    root: RootNode,
    *,
    collect_root: Literal[True] = True,
    collect_branch: Literal[True] = True,
    collect_leaf: Literal[True] = True,
) -> dict[Path, Node]: ...


def collect_nodes(
    root: RootNode,
    *,
    collect_root: bool = True,
    collect_branch: bool = True,
    collect_leaf: bool = True,
) -> dict[Path, Node]:
    """Collect all nodes under `root` into a dictionary and return it.

    Dict keys are `node.dst`, values are the corresponding nodes.

    Args:
        root (RootNode): The root node of the node tree to be collected.
        collect_root (bool): Whether to collect the root node, default to `True`.
        collect_branch (bool): Whether to collect branch nodes, default to `True`.
        collect_leaf (bool): Whether to collect leaf nodes, default to `True`.

    Returns:
        dict[Path, Node]: The dictionary containing all nodes under `root`.
    """
    nodes: dict[Path, Node] = {}

    @overload
    def add_node(node: RootNode) -> RootNode: ...

    @overload
    def add_node(node: BranchNode) -> BranchNode: ...

    @overload
    def add_node(node: LeafNode) -> LeafNode: ...

    def add_node(node: Node) -> Node:
        nodes[node.dst] = node
        return node

    on_root = add_node if collect_root else None
    on_branch = add_node if collect_branch else None
    on_leaf = add_node if collect_leaf else None

    callbacks = Callbacks(root=on_root, branch=on_branch, leaf=on_leaf)
    walk_tree(root, callbacks=callbacks, order=Order.PRE, update=False)

    return nodes
