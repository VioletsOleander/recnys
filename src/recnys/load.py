"""Provide functions for loading YAML configuration and variables files."""

import logging
from typing import TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = [
    "ConfigValue",
    "LoadedConfig",
    "LoadedVariables",
    "load_config",
    "load_variables",
]

if TYPE_CHECKING:
    type ConfigValue = dict[str, dict[str, str] | str] | None
    type LoadedConfig = dict[str, ConfigValue]
    type LoadedVariables = dict[str, str]


def _load_yaml(file_path: Path) -> dict:
    try:
        with file_path.open("r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.exception("File %s not found", file_path)
        raise


def load_config(file_path: Path) -> LoadedConfig:
    """Load YAML configuration from the specified file path.

    Args:
        file_path (Path): The path to the YAML configuration file.

    Returns:
        LoadedConfig: The loaded configuration as a dictionary.

    Raises:
        FileNotFoundError: If the configuration file does not exist at the specified path.
    """
    logger.info("Loading configuration from %s", file_path)
    return _load_yaml(file_path)


def load_variables(file_path: Path) -> LoadedVariables:
    """Load variables from the specified file path.

    Args:
        file_path (Path): The path to the variables file.

    Returns:
        LoadedVariables: The loaded variables as a dictionary.

    Raises:
        FileNotFoundError: If the variables file does not exist at the specified path.
    """
    logger.info("Loading variables from %s", file_path)
    return _load_yaml(file_path)
