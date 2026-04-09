from recnys.backend.model import BranchNode, LeafNode, RootNode

__all__ = ["print_subtree", "print_tree"]


def print_tree(root: RootNode, *, verbose: bool = False) -> None:
    message = str(root.dst)
    if verbose:
        message += " (root)"

    print(message)

    for i, child in enumerate(root.children.values()):
        is_last = i == len(root.children) - 1
        print_subtree(child, prefix="", is_last=is_last, verbose=verbose)


def print_subtree(
    node: BranchNode | LeafNode, prefix: str, *, is_last: bool, verbose: bool
) -> None:
    marker = "└── " if is_last else "├── "

    message = f"{prefix}{marker}{node.dst}"
    if verbose:
        suffix = (
            f" (leaf, src: {node.src}, op: {node.op})"
            if isinstance(node, LeafNode)
            else f" (branch, op: {node.op})"
        )
        message += suffix

    print(message)

    if isinstance(node, LeafNode):
        return

    next_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children.values()):
        is_last = i == len(node.children) - 1
        print_subtree(child, prefix=next_prefix, is_last=is_last, verbose=verbose)
