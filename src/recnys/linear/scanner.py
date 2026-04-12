"""Provide functions for scanning YAML configuration and variables data.

The scanning stage transforms the raw YAML configuration/variables file into
`ScannedConfig`/`ScannedVariables`, performing basic validation on the data.

This stage can be analogized to the lexical analysis stage in a compilation pipeline.
"""

import logging
from typing import overload

from pydantic import ValidationError

from .model import ScannedConfig, ScannedVariables

__all__ = ["scan_config", "scan_variables"]

logger = logging.getLogger(__name__)


@overload
def _validate_data(cls: type[ScannedConfig], data: dict, note: str) -> ScannedConfig: ...


@overload
def _validate_data(cls: type[ScannedVariables], data: dict, note: str) -> ScannedVariables: ...


def _validate_data(
    cls: type[ScannedConfig | ScannedVariables], data: dict, note: str
) -> ScannedConfig | ScannedVariables:
    try:
        return cls(data)
    except ValidationError as e:
        e.add_note(note)
        raise


def scan_config(loaded_config: dict) -> ScannedConfig:
    """Transform YAML configuration data into a `ScannedConfig` object.

    Args:
        loaded_config (dict): The YAML configuration data.

    Returns:
        ScannedConfig: The scanned configuration.

    Raises:
        ValidationError: If the given configuration data does not conform to the expected schema.
    """
    logger.debug("Scanning configuration data.")

    data = _validate_data(
        cls=ScannedConfig,
        data=loaded_config,
        note="Hint: Please check the contents of your recnys.yaml file.",
    )

    logger.debug("Scanned configuration: %s", data)
    return data


def scan_variables(loaded_variables: dict) -> ScannedVariables:
    """Transform YAML variables data into a `ScannedVariables` object.

    Args:
        loaded_variables (dict): The YAML variables data.

    Returns:
        ScannedVariables: The scanned variables.

    Raises:
        ValidationError: If the given variables data does not conform to the expected schema.
    """
    logger.debug("Scanning variables data.")

    data = _validate_data(
        cls=ScannedVariables,
        data=loaded_variables,
        note="Hint: Please check the contents of your variables.yaml file.",
    )

    logger.debug("Scanned variables: %s", data)
    return data
