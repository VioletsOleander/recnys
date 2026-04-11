from pathlib import Path

from pydantic import BaseModel

from .platform import Platform

__all__ = ["Paths", "get_paths"]


class Paths(BaseModel):
    """Paths holds various paths used in the application."""

    # Dirs
    home: Path
    config_dir: Path
    repo_dir: Path
    data_dir: Path

    # Files
    log_file: Path
    ctree_file: Path
    dtree_file: Path
    ctree_backup_file: Path
    dtree_backup_file: Path
    record_file: Path
    recnys_file: Path
    variables_file: Path


def get_paths(platform: Platform) -> Paths:
    """Construct and return the Paths object with appropriate file paths."""
    # Dirs
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

    # Files
    log_file = data_dir / "recnys.log"
    record_file = data_dir / "record.json"
    ctree_file = data_dir / "prev_ctree.json"
    dtree_file = data_dir / "prev_dtree.json"
    ctree_backup_file = ctree_file.with_suffix(".json.backup")
    dtree_backup_file = dtree_file.with_suffix(".json.backup")
    recnys_file = repo_dir / "recnys.yaml"
    variables_file = repo_dir / "variables.yaml"

    paths = Paths(
        home=home,
        config_dir=config_dir,
        repo_dir=repo_dir,
        data_dir=data_dir,
        log_file=log_file,
        ctree_file=ctree_file,
        dtree_file=dtree_file,
        ctree_backup_file=ctree_backup_file,
        dtree_backup_file=dtree_backup_file,
        record_file=record_file,
        recnys_file=recnys_file,
        variables_file=variables_file,
    )
    _ensure_exist(paths)

    return paths


def _ensure_exist(paths: Paths) -> None:
    """Ensure that the necessary directories and files exist."""
    paths.data_dir.mkdir(exist_ok=True)

    gitignore = paths.data_dir / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Created by recnys\n*\n", encoding="utf-8")
