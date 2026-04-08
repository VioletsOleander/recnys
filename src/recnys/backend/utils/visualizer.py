from recnys.backend.model import BranchNode, LeafNode, RootNode

__all__ = ["print_subtree", "print_tree"]


def print_tree(root: RootNode) -> None:
    print(root.dst)

    for i, child in enumerate(root.children.values()):
        is_last = i == len(root.children) - 1
        print_subtree(child, prefix="", is_last=is_last)


def print_subtree(node: BranchNode | LeafNode, prefix: str, *, is_last: bool) -> None:
    marker = "└── " if is_last else "├── "
    print(f"{prefix}{marker}{node.dst}")

    if isinstance(node, LeafNode):
        return

    next_prefix = prefix + ("    " if is_last else "│   ")
    for i, child in enumerate(node.children.values()):
        is_last = i == len(node.children) - 1
        print_subtree(child, prefix=next_prefix, is_last=is_last)
