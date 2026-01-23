"""Provide `load` for loading YAML configuration files."""

import logging
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["LoadedConfig", "load"]

type LoadedConfig = dict[str, None | dict[str, dict | str]]


def load(file_path: Path) -> LoadedConfig:
    """Load YAML configuration from the specified file path.

    Args:
        file_path (Path): The path to the YAML configuration file.

    Returns:
        LoadedConfig: The loaded configuration as a dictionary.
    """
    with file_path.open("r") as file:
        logger.info("Loading configuration from %s", file_path)
        return yaml.safe_load(file)
