import os
from typing import TYPE_CHECKING

from .constants import RECNYS_FCONTENT, VARIABLES_FCONTENT, LazyConstants

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem

__all__ = ["create_recnys_file", "create_source_files", "create_variables_file"]


def change_cwd(filesystem: FakeFilesystem) -> Path:
    """Create and change the current working directory to the test repo.

    Return the new current working directory.
    """
    filesystem.create_dir(LazyConstants.cwd)
    os.chdir(LazyConstants.cwd)
    return LazyConstants.cwd


def create_recnys_file(filesystem: FakeFilesystem) -> Path:
    """Create the recnys file in the fake filesystem.

    Return the path to the created recnys file.
    """
    f = LazyConstants.recnys_file
    filesystem.create_file(f, contents=RECNYS_FCONTENT)

    return f


def create_variables_file(filesystem: FakeFilesystem) -> Path:
    """Create the variables file in the fake filesystem.

    Return the path to the created variables file.
    """
    f = LazyConstants.variables_file
    filesystem.create_file(f, contents=VARIABLES_FCONTENT)

    return f


def create_source_files(filesystem: FakeFilesystem) -> None:
    """Create the source files in the fake filesystem."""
    for f in LazyConstants.files_to_create:
        filesystem.create_file(f)
