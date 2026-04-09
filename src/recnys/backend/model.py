"""Provide node models."""

from enum import Enum, auto
from pathlib import Path  # noqa: TC003, Path is required by pydantic in runtime

from pydantic import BaseModel

__all__ = ["BranchNode", "LeafNode", "Node", "Operation", "RootNode"]

type Node = RootNode | BranchNode | LeafNode


class Operation(Enum):
    """Category of an operation.

    Attributes:
        CREATE: Create a node at the destination path, corresponding to mkdir.
            No effect if the node already exists.
        RENDER: Render a node from the source path to the destination path,
            corresponding to render and copy file.
        COPY: Copy a node from the source path to the destination path,
            corresponding to copy dir or copy file.
        LINK: Create a symbolic link from the source path to the destination path,
            corresponding to symlink dir or symlink file.
        REMOVE: Remove a node at the destination path,
            corresponding to remove dir or remove file.
        UNLINK: Remove a symbolic link at the destination path,
            corresponding to unlink dir or unlink file.
    """

    CREATE = auto()
    RENDER = auto()
    COPY = auto()
    LINK = auto()
    REMOVE = auto()
    UNLINK = auto()


class RootNode(BaseModel):
    """The root node of the node tree.

    Attributes:
        dst (Path): The destination path of the root node, which should be the home directory.
        op (Operation): The operation to be performed on the root node. Always CREATE.
        children (dict[Path, BranchNode | LeafNode]): The child nodes of the root node,
            keyed by their destination paths.
    """

    dst: Path
    op: Operation = Operation.CREATE
    children: dict[Path, BranchNode | LeafNode] = {}


class BranchNode(BaseModel):
    """A branch node in the node tree.

    Attributes:
        dst (Path): The destination path of the branch node.
        op (Operation): The operation to be performed on the branch node. Always CREATE.
        children (dict[Path, BranchNode | LeafNode]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    op: Operation = Operation.CREATE
    children: dict[Path, BranchNode | LeafNode] = {}


class LeafNode(BaseModel):
    """A leaf node in the node tree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
        op (Operation): The operation to be performed on the leaf node.
    """

    src: Path
    dst: Path
    op: Operation
