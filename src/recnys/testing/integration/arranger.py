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
    # add_real_file seems to have problem when simulating different system's filesystem
    # so using content to create files instead of adding real files
    fs.pause()
    recnys_content = (resources_dir / RECNYS_FNAME).read_text(encoding="utf-8")
    variables_content = (resources_dir / VARIABLES_FNAME).read_text(encoding="utf-8")
    fs.resume()

    fs.create_file(Const.recnys_file, contents=recnys_content)
    fs.create_file(Const.variables_file, contents=variables_content)


def create_source_files(fs: FakeFilesystem) -> None:
    """Create the source files in the fake filesystem."""
    for f in Const.files_to_create:
        fs.create_file(f, contents=f"Content of {f.name}")
