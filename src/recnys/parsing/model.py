"""Provide node models."""

from enum import Enum, auto
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["BranchNode", "LeafNode", "Operation", "RootNode"]


class Operation(Enum):
    """Category of an operation.

    Attributes:
        CREATE: Create a node at the destination path.
        RENDER: Render a node from the source path to the destination path.
        COPY: Copy a node from the source path to the destination path.
        LINK: Create a symbolic link from the source path to the destination path.
        REMOVE: Remove a node at the destination path.
        UNLINK: Remove a symbolic link at the destination path.
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
        parent (RootNode | BranchNode): The parent node of the branch node.
        children (dict[Path, BranchNode | LeafNode]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    op: Operation = Operation.CREATE
    parent: RootNode | BranchNode
    children: dict[Path, BranchNode | LeafNode] = {}


class LeafNode(BaseModel):
    """A leaf node in the node tree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
        op (Operation): The operation to be performed on the leaf node.
        parent (RootNode | BranchNode): The parent node of the leaf node.
    """

    src: Path
    dst: Path
    op: Operation
    parent: RootNode | BranchNode
