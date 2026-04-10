import logging
from pathlib import Path
from typing import overload

from pydantic import ValidationError

from recnys.backend.model import BranchNode, LeafNode, Node, RootNode

logger = logging.getLogger(__name__)

__all__ = ["deserialize_tree", "serialize_tree"]


def serialize_tree(root: RootNode, file_path: Path) -> None:
    """Dump the given root node to a json file."""
    logger.debug("Serializing data to %s", file_path)
    json_data = root.model_dump_json(indent=2)
    file_path.write_text(json_data, encoding="utf-8")
    logger.debug("Successfully serialized data to %s", file_path)


def deserialize_tree(file_path: Path) -> RootNode:
    """Load a root node from a json file."""
    try:
        logger.debug("Deserializing data from %s", file_path)
        data = file_path.read_text(encoding="utf-8")
        root = RootNode.model_validate_json(data)
        root = _concretize(root)
    except ValidationError as e:
        message = (
            f"Hint: Data in {file_path} is corrupted, please use backup file to recover it. "
            "If backup file is not available, please delete it."
        )
        e.add_note(message)
        raise
    else:
        logger.debug("Successfully deserialized data from %s", file_path)
        return root


@overload
def _concretize(node: RootNode) -> RootNode: ...


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
