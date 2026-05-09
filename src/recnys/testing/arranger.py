"""Shared arrangers for unit and integration tests."""

import os
from pathlib import Path
from typing import TYPE_CHECKING

from .constants import RECNYS_FNAME, VARIABLES_FNAME, LazyConstants

if TYPE_CHECKING:
    from collections.abc import Sequence

    from pyfakefs.fake_filesystem import FakeFilesystem

__all__ = ["create_config_files", "create_cwd", "create_source_files"]


def create_cwd(fs: FakeFilesystem) -> None:
    """Create and change the current working directory to the test repo in the fake filesystem."""
    fs.create_dir(LazyConstants.cwd)
    os.chdir(LazyConstants.cwd)


def create_config_files(fs: FakeFilesystem, resources_dir: Path) -> None:
    """Create the recnys.yaml and variables.yaml files in the fake filesystem."""
    # fs.add_real_file seems to have problem when simulating different system's filesystem
    # so using content to create files instead of adding real files
    fs.pause()
    recnys_content = (resources_dir / RECNYS_FNAME).read_text(encoding="utf-8")
    variables_content = (resources_dir / VARIABLES_FNAME).read_text(encoding="utf-8")
    fs.resume()

    fs.create_file(LazyConstants.recnys_file, contents=recnys_content)
    fs.create_file(LazyConstants.variables_file, contents=variables_content)


def create_source_files(fs: FakeFilesystem, source_files: Sequence[str]) -> None:
    """Create the source files in the fake filesystem.

    Expect `source_files` to be a sequence of filenames. All files will be created under current
    working directory.
    """
    for f in source_files:
        fs.create_file(Path.cwd() / f, contents=f"Content of {f}")
