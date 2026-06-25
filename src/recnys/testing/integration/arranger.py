from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem

__all__ = ["create_config_files"]


def create_config_files(fs: FakeFilesystem, recnys_file: Path, variables_file: Path) -> None:
    """Create recnys.yaml and variables.yaml under cwd in the fake filesystem."""
    # fs.add_real_file seems to have problem when simulating different system's filesystem
    # so using content to create files instead of adding real files
    fs.pause()
    recnys_content = recnys_file.read_text(encoding="utf-8")
    variables_content = variables_file.read_text(encoding="utf-8")
    fs.resume()

    fs.create_file("recnys.yaml", contents=recnys_content)
    fs.create_file("variables.yaml", contents=variables_content)
