from enum import StrEnum, auto
from pathlib import Path  # noqa: TC003, Path is required by pydantic in runtime

from pydantic import BaseModel

__all__ = [
    "BranchNode",
    "CLeafOp",
    "CTree",
    "DBranchOp",
    "DLeafOp",
    "DTree",
    "LeafNode",
    "LeafOp",
    "Tree",
]

type Tree = CTree | DTree
type Node = BranchNode | LeafNode
type LeafOp = CLeafOp | DLeafOp


class CTree(BaseModel):
    """Creation tree.

    Attributes:
        root (BranchNode): The root node of the creation tree.
        ops (dict[Path, CLeafOp]): The operations for leaf nodes in the creation tree, keyed by
            their destination paths.
    """

    root: BranchNode
    ops: dict[Path, CLeafOp] = {}


class DTree(BaseModel):
    """Deletion tree.

    Attributes:
        root (BranchNode): The root node of the deletion tree.
        ops (dict[Path, DBranchOp | DLeafOp]): The operations for each node in the deletion tree, keyed by
            their destination paths.
    """

    root: BranchNode
    ops: dict[Path, DBranchOp | DLeafOp] = {}


class BranchNode(BaseModel):
    """A branch node in a tree.

    Attributes:
        dst (Path): The destination path of the branch node.
            If the branch node is the root node, dst should be the home directory.
        children (dict[Path, BranchNode | LeafNode]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    children: dict[Path, BranchNode | LeafNode] = {}


class LeafNode(BaseModel):
    """A leaf node in a tree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
    """

    src: Path
    dst: Path


class CLeafOp(StrEnum):
    """Category of an operation for leaf nodes in ctree.

    Attributes:
        COPY: Copy a node from the source path to the destination path.
            Corresponds to `Path.copy` or overwrite file.
        LINK: Create a symbolic link from the source path to the destination path.
            Corresponds to `Path.symlink_to`.
        RENDER: Render a node from the source path to the destination path.
            Corresponds to render and copy/overwrite file.
    """

    COPY = auto()
    LINK = auto()
    RENDER = auto()


class DBranchOp(StrEnum):
    """Category of an operation for branch nodes in dtree.

    Attributes:
        NOP: No operation.
        REMOVE: Remove a node at the destination path.
            Corresponds to `Path.rmdir`, no effect if there are existing files under the node.
    """

    NOP = auto()
    REMOVE = auto()


class DLeafOp(StrEnum):
    """Category of an operation for leaf nodes in dtree.

    Attributes:
        NOP: No operation.
        UNLINK: Remove a file or symbolic link at the destination path.
            Corresponds to `Path.unlink`, no effect if the node does not exist.
    """

    NOP = auto()
    UNLINK = auto()
