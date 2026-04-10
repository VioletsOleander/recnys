from pathlib import Path  # noqa: TC003, Path is required by pydantic in runtime

from pydantic import BaseModel

from .op import CBranchOp, CLeafOp, DBranchOp, DLeafOp

__all__ = ["CBranchNode", "CLeafNode", "CRootNode", "DBranchNode", "DLeafNode", "DRootNode"]

# because of type erasure of generics, isinstance() does not work for concretized generic types
# we have to maintain the metadata of the concrete types manually, which, for other languages like
# cpp, is maintained by the compiler.


class RootNode[B: (CBranchOp, DBranchOp), L: (CLeafOp, DLeafOp)](BaseModel):
    """The root node of a tree.

    Corresponds to the home directory, which should always exist.

    Attributes:
        dst (Path): The destination path of the root node, which should be the home directory.
        children (dict[Path, BranchNode[B, L] | LeafNode[B, L]]): The child nodes of the root node,
            keyed by their destination paths.
    """

    dst: Path
    children: dict[Path, BranchNode[B, L] | LeafNode[L]] = {}


class BranchNode[B: (CBranchOp, DBranchOp), L: (CLeafOp, DLeafOp)](BaseModel):
    """A branch node in a tree.

    Attributes:
        dst (Path): The destination path of the branch node.
        op (B): The operation to be performed on the branch node.
        children (dict[Path, BranchNode[B, L] | LeafNode[B, L]]): The child nodes of the branch node,
            keyed by their destination paths.
    """

    dst: Path
    op: B
    children: dict[Path, BranchNode[B, L] | LeafNode[L]] = {}


class LeafNode[L: (CLeafOp, DLeafOp)](BaseModel):
    """A leaf node in a tree.

    Attributes:
        src (Path): The source path of the leaf node.
        dst (Path): The destination path of the leaf node.
        op (L): The operation to be performed on the leaf node.
    """

    src: Path
    dst: Path
    op: L


# Generic[concrete-type] does not support isinstance() because all
# concretized generic types are considered the same at runtime.
# Since we rely on isinstance(), we define subclasses for each concrete type combination.


class CRootNode(RootNode[CBranchOp, CLeafOp]):
    """The root node of a ctree."""


class DRootNode(RootNode[DBranchOp, DLeafOp]):
    """The root node of a dtree."""


class CBranchNode(BranchNode[CBranchOp, CLeafOp]):
    """A branch node in a ctree."""


class DBranchNode(BranchNode[DBranchOp, DLeafOp]):
    """A branch node in a dtree."""


class CLeafNode(LeafNode[CLeafOp]):
    """A leaf node in a ctree."""


class DLeafNode(LeafNode[DLeafOp]):
    """A leaf node in a dtree."""
