from enum import Enum, auto
from pathlib import Path

from pydantic import BaseModel

type Operation = CreateOperation | DeleteOperation


class DeleteOperationCode(Enum):
    """The category of a delete operation.

    Attributes:
        UNLINK: Remove a symbolic link at the destination path.
        RMDIR: Remove a directory at the destination path.
        RMFILE: Remove a file at the destination path.
    """

    UNLINK = auto()
    RMDIR = auto()
    RMFILE = auto()


class DeleteOperation(BaseModel):
    dest: Path
    code: DeleteOperationCode


class CreateOperationCode(Enum):
    """The category of a create operation.

    Attributes:
        COPY: Copy the source file/directory to the destination.
        RENDER: Render the source file to the destination.
        SYMLINK: Create a symbolic link from the source path to the destination path.
    """

    COPY = auto()
    RENDER = auto()
    SYMLINK = auto()


class CreateOperation(BaseModel):
    src: Path
    dest: Path
    code: CreateOperationCode
