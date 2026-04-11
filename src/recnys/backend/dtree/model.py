from enum import StrEnum, auto
from pathlib import Path  # noqa: TC003, Path is required by pydantic in runtime

from pydantic import BaseModel

__all__ = ["DBranchNode", "DBranchOp", "DLeafNode", "DLeafOp", "DRootNode"]


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


class DRootNode(BaseModel):
    """The root node of a dtree.

    Corresponds to the home directory, which should always exist.

    Attributes:
        dst (Path): The destination path of the root node, which should be the home directory.
        children (dict[Path, DBranchNode | DLeafNode]): The child nodes of the root node,
            keyed by their destination paths.
    """

    dst: Path
    children: dict[Path, DBranchNode | DLeafNode] = {}


class DBranchNode(BaseModel):
    """A branch node in a dtree.

    Attributes:
        dst (Path): The destination path of the branch node.
        op (DBranchOp): The operation to be performed on the branch node.
        children (dict[Path, DBranchNode | DLeafNode]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    op: DBranchOp
    children: dict[Path, DBranchNode | DLeafNode] = {}


class DLeafNode(BaseModel):
    """A leaf node in a dtree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
        op (DLeafOp): The operation to be performed on the leaf node.
    """

    src: Path
    dst: Path
    op: DLeafOp
