"""Provide `load` and `parse` for loading and parsing sync configuration."""

import logging
from typing import TYPE_CHECKING

import yaml

from .task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["load", "parse"]


def load(file_path: Path) -> dict[str, dict[str, object]]:
    """Load YAML configuration from the specified file path.

    Args:
        file_path (Path): The path to the YAML configuration file.

    Returns:
        dict[str, dict[str, object]]: The loaded configuration as a dictionary.
    """
    with file_path.open("r") as file:
        logger.info("Loading configuration from %s", file_path)
        return yaml.safe_load(file)


def parse(config: dict[str, dict[str, object]]) -> list[SyncTask]:
    """Parse given configuration dictionary into a list of SyncTask objects.

    Expect the given configuration dictionary to contain the mapping between
    source paths and their corresponding synchronization rules.

    Each entry in the configuration dictionary will be parsed to one synchronization task.

    Args:
        config (dict[str, dict[str, object]]): The configuration dictionary.

    Returns:
        list[SyncTask]: A list of SyncTask objects parsed from the configuration.
    """
    sync_tasks = []

    for sync_src, sync_rule in config.items():
        logger.info("Parsing entry for source: %s", sync_src)

        src = Src(sync_src)

        sync_dst = sync_rule.get("dest")
        match sync_dst:
            case None:
                dst = Dst(src=src)
            case dict() as d:
                linux = d.get("linux")
                windows = d.get("windows")
                dst = Dst(linux=linux, windows=windows, src=src)
            case _:
                raise ValueError(f"Invalid destination format for source {sync_src}: {sync_dst}")

        sync_policy = sync_rule.get("policy")
        match sync_policy:
            case "overwrite" | None:
                policy = Policy.OVERWRITE
            case "source":
                policy = Policy.SOURCE
            case _:
                raise ValueError(
                    f"Invalid policy value for source {sync_src}: {sync_policy}"
                    "The valid options are 'overwrite' or 'source'."
                )

        sync_tasks.append(SyncTask(src=src, dst=dst, policy=policy))
        logger.info("Added SyncTask: %s", sync_tasks[-1])

    return sync_tasks
