from pathlib import Path

from pydantic import BaseModel

from .platform import Platform

__all__ = ["Paths", "make_paths"]


class Paths(BaseModel):
    """Paths holds various paths used in the application."""

    home: Path
    config_dir: Path
    repo_dir: Path
    data_dir: Path
    log_file: Path
    tree_file: Path
    record_file: Path
    recnys_file: Path
    variables_file: Path


def make_paths(platform: Platform) -> Paths:
    """Construct and return the Paths object with appropriate file paths."""
    home = Path.home()
    match platform:
        case Platform.LINUX:
            config_dir = Path.home() / ".config/"
        case Platform.WINDOWS:
            config_dir = Path.home() / "AppData/Roaming/"
        case _:
            raise NotImplementedError(f"Unsupported platform: {platform}")

    repo_dir = Path.cwd()
    data_dir = repo_dir / ".recnys"

    data_dir.mkdir(exist_ok=True)

    gitignore = data_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Created by recnys\n*\n", encoding="utf-8")

    return Paths(
        home=home,
        config_dir=config_dir,
        repo_dir=repo_dir,
        data_dir=data_dir,
        log_file=data_dir / "recnys.log",
        record_file=data_dir / "record.json",
        tree_file=data_dir / "prev_tree.json",
        recnys_file=repo_dir / "recnys.yaml",
        variables_file=repo_dir / "variables.yaml",
    )
