import os
from typing import TYPE_CHECKING

from .constants import LazyConstants

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem


def change_cwd(filesystem: FakeFilesystem) -> Path:
    """Create and change the current working directory to the test repo.

    Return the new current working directory.
    """
    filesystem.create_dir(LazyConstants.cwd)
    os.chdir(LazyConstants.cwd)
    return LazyConstants.cwd


def create_config_files(filesystem: FakeFilesystem, resources_dir: Path) -> None:
    """Create the recnys.yaml and variables.yaml files in the fake filesystem."""
    filesystem.add_real_file(
        resources_dir / LazyConstants.recnys_file.name, target_path=LazyConstants.recnys_file
    )
    filesystem.add_real_file(
        resources_dir / LazyConstants.variables_file.name, target_path=LazyConstants.variables_file
    )


def create_data_files(filesystem: FakeFilesystem, resources_dir: Path, system: str) -> None:
    """Create the necessary data files in the fake filesystem based on the system."""
    match system:
        case "Linux":
            real_file = resources_dir / "linux" / "prev_creation_tree.json"
        case "Windows":
            real_file = resources_dir / "windows" / "prev_creation_tree.json"
        case _:
            raise ValueError(f"Unsupported system: {system}")

    filesystem.add_real_file(
        real_file, target_path=LazyConstants.data_dir / "prev_creation_tree.json"
    )


def create_source_files(filesystem: FakeFilesystem) -> None:
    """Create the source files in the fake filesystem."""
    for f in LazyConstants.files_to_create:
        filesystem.create_file(f)
