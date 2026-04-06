from pathlib import Path

from pydantic import BaseModel

__all__ = ["Paths", "make_paths"]


class Paths(BaseModel):
    """Paths holds various paths used in the application."""

    home: Path
    repo_dir: Path
    data_dir: Path
    log_file: Path
    record_file: Path
    config_file: Path
    variables_file: Path


def make_paths() -> Paths:
    """Construct and return the Paths object with appropriate file paths."""
    repo_dir = Path.cwd()
    data_dir = repo_dir / ".recnys"
    data_dir.mkdir(exist_ok=True)

    return Paths(
        home=Path.home(),
        repo_dir=repo_dir,
        data_dir=data_dir,
        log_file=data_dir / "log.txt",
        record_file=data_dir / "record.json",
        config_file=repo_dir / "recnys.yaml",
        variables_file=repo_dir / "variables.yaml",
    )
