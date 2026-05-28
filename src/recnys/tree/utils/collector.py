from typing import TYPE_CHECKING, Literal, overload

from .walker import Callbacks, VisitOrder, walk_tree

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.tree.model import BranchNode, LeafNode, Node, Tree

__all__ = ["collect_nodes"]

# The type invariance of dict makes dict[Path, LeafNode (or BranchNode)] not assignable to dict[Path, Node]
# suppress the type error here, because I think current implementation is fairly good enough


@overload
def collect_nodes(tree: Tree, *, collect_leaf: Literal[False]) -> dict[Path, BranchNode]: ...  # type: ignore[ty:invalid-overload]


@overload
def collect_nodes(tree: Tree, *, collect_branch: Literal[False]) -> dict[Path, LeafNode]: ...  # type: ignore[ty:invalid-overload]


@overload
def collect_nodes(tree: Tree) -> dict[Path, Node]: ...


def collect_nodes(
    tree: Tree, *, collect_branch: bool = True, collect_leaf: bool = True
) -> dict[Path, Node]:
    """Collect non-root nodes under `tree` into a dictionary and return it.

    Dict keys are `node.dst`, values are the corresponding nodes.

    Args:
        tree (Tree): The tree whose nodes are to be collected.
        collect_branch (bool): Whether to collect branch nodes, default to `True`.
        collect_leaf (bool): Whether to collect leaf nodes, default to `True`.

    Returns:
        dict[Path, Node]: The dictionary containing all non-root nodes under `tree`.
    """
    nodes: dict[Path, Node] = {}

    def add_node(node: Node) -> None:
        nodes[node.dst] = node

    on_branch = add_node if collect_branch else None
    on_leaf = add_node if collect_leaf else None

    callbacks = Callbacks(branch=on_branch, leaf=on_leaf)
    walk_tree(tree, callbacks=callbacks, order=VisitOrder.PRE)

    return nodes
