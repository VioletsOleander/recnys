"""Provide functions for loading raw data from files."""

import logging
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["load_yaml"]

logger = logging.getLogger(__name__)


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
    logger.debug("Loading YAML file %s", file_path)

    try:
        with file_path.open("r") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError as e:
        e.add_note(note)
        raise
    else:
        logger.debug("Loaded data: %s", data)
        return data
