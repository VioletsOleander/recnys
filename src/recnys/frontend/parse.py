"""Provide `parse` for parsing loaded configuration into SyncTask objects."""

import logging
from typing import TYPE_CHECKING

from .task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from .load import LoadedConfig

logger = logging.getLogger(__name__)

__all__ = ["parse"]


def _parse_value(sync_src: str, sync_rule: dict) -> tuple[Dst, Policy]:
    sync_dst = sync_rule.get("dest")
    match sync_dst:
        case None:
            dst = Dst(src=sync_src)
        case dict():
            linux = sync_dst.get("linux")
            windows = sync_dst.get("windows")
            dst = Dst(src=sync_src, linux=linux, windows=windows)
        case _:
            raise ValueError(f"Invalid destination format: {sync_dst}")

    sync_policy = sync_rule.get("policy")
    match sync_policy:
        case None:
            policy = Policy.DEFAULT
        case "overwrite":
            policy = Policy.OVERWRITE
        case "source":
            policy = Policy.SOURCE
        case _:
            raise ValueError(
                f"Invalid policy value: {sync_policy} The valid options are 'overwrite' or 'source'."
            )

    return dst, policy


def parse(config: LoadedConfig) -> list[SyncTask]:
    """Parse given configuration dictionary into a list of SyncTask objects.

    Expect the given configuration dictionary to have the following structure:

    ```python
    {
        "<source_path1>" : {
            "dest": {"linux": "<dest_path1_linux>", "windows": "<dest_path1_windows>"},
            "policy": "<policy_value>"
        },
        "<source_path2>": None,
        ...
    }
    ```

    All paths in the configuration should be relative paths from the parent directory of the
    configuration file.

    If an empty string "" is given as destination path for a platform, it means no syncing
    for that platform.

    Source paths can point to either files or directories, determined by
    whether it is ended with a '/' (directory) or not (file).

    The value for each source path represents the syncing rule, which can be either:
    - `None`, in which case default values for `dst` and `policy` will be used.
    - A dictionary containing optional `dest` and `policy` keys.

    For file, the default dest path for linux and windows platform are both `~/<source_path>`.

    For directory, the default dest paths are:
    - linux platform: `~/.config/<source_path>/`
    - windows platform: `~/AppData/Roaming/<source_path>`

    For example, `helix/` will be synced to `~/AppData/Roaming/helix/` on windows platform,
    and be synced to `~/.config/helix/` on linux platform, if no destination is specified.

    Policy can be either:
    - `overwrite`: overwrite the destination with the source (default).
    - `source`: prepend a source statement to the destination file.

    The returned SyncTask objects will have all paths resolved to absolute paths.

    Args:
        config (LoadedConfig): The loaded configuration dictionary.

    Returns:
        list[SyncTask]: A list of SyncTask objects parsed from the configuration.
    """
    sync_tasks = []

    for sync_src, sync_rule in config.items():
        logger.info("Parsing entry for source: %s", sync_src)
        if not isinstance(sync_src, str):
            raise TypeError(f"Source path must be a string, got: {type(sync_src)}")

        src = Src(sync_src)
        match sync_rule:
            case None:
                dst = Dst(sync_src)
                policy = Policy.DEFAULT
            case dict():
                dst, policy = _parse_value(sync_src, sync_rule)
            case _:
                raise TypeError(
                    f"Value for source path must be either None or a dict, got: {type(sync_rule)}"
                )

        sync_tasks.append(SyncTask(src=src, dst=dst, policy=policy))
        logger.info("Successfully parsed SyncTask for source: %s", sync_src)

    return sync_tasks
