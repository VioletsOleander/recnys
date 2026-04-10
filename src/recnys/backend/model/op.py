from enum import StrEnum, auto


class CBranchOp(StrEnum):
    """Category of an operation for branch nodes in ctree.

    Attributes:
        NOP: No operation.
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
