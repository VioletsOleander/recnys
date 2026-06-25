from typing import NamedTuple

__all__ = ["File", "Symlink"]


class Symlink(NamedTuple):
    """A symlink node.

    Attributes:
        src (str): Source path, relative to cwd.
        dst (str): Destination path, relative to home.
    """

    src: str
    dst: str


class File(NamedTuple):
    """A file node.

    Attributes:
        path (str): File path. For source file, relative to cwd. For target file, relative to home.
        content (str): File content.
    """

    path: str
    content: str
