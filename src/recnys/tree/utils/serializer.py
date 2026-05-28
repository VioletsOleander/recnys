import logging
from pathlib import Path
from typing import overload

from pydantic import ValidationError

from recnys.tree.model import BranchNode, CTree, DTree, LeafNode, Node, Tree

__all__ = ["deserialize_tree", "serialize_tree"]

logger = logging.getLogger(__name__)


def serialize_tree(tree: Tree, f: Path) -> None:
    """Dump a tree to a json file.

    Attributes:
        tree (Tree): The tree to be dumped to the json file.
        f (Path): The path to the json file to dump the tree to.
    """
    logger.debug("Serializing data to %s", f)

    content = tree.model_dump_json(indent=2)
    f.write_text(content, encoding="utf-8")

    logger.debug("Serialized data to %s", f)


def deserialize_tree[T: (CTree, DTree)](cls: type[T], f: Path) -> T:
    """Load a tree from a json file.

    Attributes:
        cls (type[T]): The type of the tree to be loaded, either CTree or DTree.
        f (Path): The path to the json file to load the tree from.

    Returns:
        T: The tree loaded from the json file, either CTree or DTree.
    """
    logger.debug("Deserializing data from %s", f)

    try:
        content = f.read_text(encoding="utf-8")
        tree = cls.model_validate_json(content)
        tree.root = _concretize(tree.root)
        tree.ops = {Path(dst): op for dst, op in tree.ops.items()}  # type: ignore[ty:invalid-assignment]
    except ValidationError as e:
        message = (
            f"Hint: Data in {f} is corrupted, please use backup file to recover it. "
            "If backup file is not available, please delete it."
        )
        e.add_note(message)
        raise
    else:
        logger.debug("Deserialized data from %s", f)
        return tree


@overload
def _concretize(node: BranchNode) -> BranchNode: ...


@overload
def _concretize(node: LeafNode) -> LeafNode: ...


def _concretize(node: Node) -> Node:
    """Convert Path object to concrete Path objects (WindowsPath or PosixPath)."""
    if isinstance(node, LeafNode):
        node.src = Path(node.src)
        node.dst = Path(node.dst)
    else:
        node.dst = Path(node.dst)
        node.children = {Path(dst): _concretize(child) for dst, child in node.children.items()}

    return node
