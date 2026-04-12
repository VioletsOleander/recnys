"""Provide functions for loading raw data from files."""

from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["load_yaml"]


def load_yaml(file_path: Path, note: str) -> dict:
    """Load YAML data from the specified file path.

    Args:
        file_path (Path): The path to the YAML file.
        note (str): The note to be added to the exception if the file is not found.

    Returns:
        dict: The loaded YAML data.

    Raises:
        FileNotFoundError: If the YAML file does not exist at the specified path.
    """
    try:
        with file_path.open("r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        e.add_note(note)
        raise
