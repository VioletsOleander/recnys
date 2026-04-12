import os
from typing import TYPE_CHECKING

from .constants import RECNYS_FNAME, VARIABLES_FNAME
from .constants import LazyConstants as Const

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem


def change_cwd(fs: FakeFilesystem) -> Path:
    """Create and change the current working directory to the test repo.

    Return the new current working directory.
    """
    fs.create_dir(Const.cwd)
    os.chdir(Const.cwd)
    return Const.cwd


def create_config_files(fs: FakeFilesystem, resources_dir: Path) -> None:
    """Create the recnys.yaml and variables.yaml files in the fake filesystem."""
    fs.add_real_file(resources_dir / RECNYS_FNAME, target_path=Const.recnys_file)
    fs.add_real_file(resources_dir / VARIABLES_FNAME, target_path=Const.variables_file)


def create_source_files(fs: FakeFilesystem) -> None:
    """Create the source files in the fake filesystem."""
    for f in Const.files_to_create:
        fs.create_file(f)
