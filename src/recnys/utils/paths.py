from pathlib import Path

from pydantic import BaseModel

__all__ = ["Paths", "make_paths"]


class Paths(BaseModel):
    """Paths holds the file paths used in the application."""

    data_dir: Path
    log_file: Path
    config_file: Path
    variables_file: Path


def make_paths() -> Paths:
    """Construct and return the Paths object with appropriate file paths."""
    cwd = Path.cwd()

    data_dir = cwd / ".recnys"
    data_dir.mkdir(exist_ok=True)

    return Paths(
        data_dir=data_dir,
        log_file=data_dir / "recnys.log",
        config_file=cwd / "recnys.yaml",
        variables_file=cwd / "variables.yaml",
    )
