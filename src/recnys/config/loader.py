"""Provide functions for loading YAML configuration and variables files."""

import logging
from typing import TYPE_CHECKING, overload

import yaml
from pydantic import ValidationError

from .model import LoadedConfig, LoadedVariables

__all__ = ["load_config", "load_variables"]

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def _load_yaml(file_path: Path, note: str) -> dict:
    try:
        with file_path.open("r") as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        e.add_note(note)
        raise


@overload
def _validate_data(cls: type[LoadedConfig], data: dict, note: str) -> LoadedConfig: ...


@overload
def _validate_data(cls: type[LoadedVariables], data: dict, note: str) -> LoadedVariables: ...


def _validate_data(
    cls: type[LoadedConfig | LoadedVariables], data: dict, note: str
) -> LoadedConfig | LoadedVariables:
    try:
        return cls(data)
    except ValidationError as e:
        e.add_note(note)
        raise


def load_config(file_path: Path) -> LoadedConfig:
    """Load YAML configuration from the specified file path.

    Args:
        file_path (Path): The path to the YAML configuration file.

    Returns:
        LoadedConfig: The loaded configuration.

    Raises:
        FileNotFoundError: If the configuration file does not exist at the specified path.
        ValidationError: If the loaded configuration data does not conform to the expected schema.
    """
    logger.info("Loading configuration from %s", file_path)

    data = _load_yaml(
        file_path=file_path,
        note="Hint: Please run this command in the root of your dotfiles repository, "
        "where the recnys.yaml file is located.",
    )

    return _validate_data(
        cls=LoadedConfig,
        data=data,
        note="Hint: Please check the contents of your recnys.yaml file.",
    )


def load_variables(file_path: Path) -> LoadedVariables:
    """Load variables from the specified file path.

    Args:
        file_path (Path): The path to the variables file.

    Returns:
        LoadedVariables: The loaded variables.

    Raises:
        FileNotFoundError: If the variables file does not exist at the specified path.
        ValidationError: If the loaded variables data does not conform to the expected schema.
    """
    logger.info("Loading variables from %s", file_path)
    data = _load_yaml(
        file_path=file_path,
        note="Hint: Please run this command in the root of your dotfiles repository, "
        "where the variables.yaml file is located.",
    )
    return _validate_data(
        cls=LoadedVariables,
        data=data,
        note="Hint: Please check the contents of your variables.yaml file.",
    )
