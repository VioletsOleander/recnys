from enum import StrEnum, auto
from pathlib import Path  # noqa: TC003, Path is required by pydantic in runtime

from pydantic import BaseModel

__all__ = ["CBranchNode", "CBranchOp", "CLeafNode", "CLeafOp", "CRootNode"]


class CBranchOp(StrEnum):
    """Category of an operation for branch nodes in ctree.

    Attributes:
        CREATE: Create a node at the destination path.
            Corresponds to `Path.mkdir`, no effect if the node already exists.
    """

    CREATE = auto()


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


class CRootNode(BaseModel):
    """The root node of a ctree.

    Corresponds to the home directory, which should always exist.

    Attributes:
        dst (Path): The destination path of the root node, which should be the home directory.
        children (dict[Path, CBranchNode | CLeafNode]): The child nodes of the root node,
            keyed by their destination paths.
    """

    dst: Path
    children: dict[Path, CBranchNode | CLeafNode] = {}


class CBranchNode(BaseModel):
    """A branch node in a tree.

    Attributes:
        dst (Path): The destination path of the branch node.
        op (CBranchOp): The operation to be performed on the branch node.
        children (dict[Path, CBranchNode | CLeafNode]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    op: CBranchOp
    children: dict[Path, CBranchNode | CLeafNode] = {}


class CLeafNode(BaseModel):
    """A leaf node in a tree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
        op (CLeafOp): The operation to be performed on the leaf node.
    """

    src: Path
    dst: Path
    op: CLeafOp
