from typing import TYPE_CHECKING

from recnys.tree.model import LeafNode

if TYPE_CHECKING:
    from pathlib import Path

    from recnys.tree.model import BranchNode, CLeafOp, DBranchOp, DLeafOp, Tree

__all__ = ["print_tree"]


def print_tree(tree: Tree, *, verbose: bool = False) -> None:
    root = tree.root

    message = f"{root.dst} (root)" if verbose else str(root.dst)
    print(message)

    for i, child in enumerate(root.children.values()):
        is_last = i == len(root.children) - 1
        _print_subtree(child, tree.ops, prefix="", is_last=is_last, verbose=verbose)


def _print_subtree(
    node: BranchNode | LeafNode,
    ops: dict[Path, CLeafOp] | dict[Path, DBranchOp | DLeafOp],
    prefix: str,
    *,
    is_last: bool,
    verbose: bool,
) -> None:
    marker = "└── " if is_last else "├── "
    message = f"{prefix}{marker}{node.dst}"

    if isinstance(node, LeafNode):
        print(f"{message} (leaf, src: {node.src}, op: {ops[node.dst]})" if verbose else message)
        return

    print(f"{message} (branch, op: {ops.get(node.dst, 'create')})" if verbose else message)

    next_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children.values()):
        is_last = i == len(node.children) - 1
        _print_subtree(child, ops, prefix=next_prefix, is_last=is_last, verbose=verbose)
