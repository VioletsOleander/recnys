"""Provide `get_default_dest` and `get_default_policy` functions for defaulting entry values."""

from recnys.parsing.model import Policy
from recnys.utils.platform import Platform

from .model import EntryKey, KeyCategory

__all__ = ["get_default_dest", "get_default_policy"]


def get_default_dest(key: EntryKey, platform: Platform) -> str:
    """Resolve and return the default destination path for the given entry key."""
    match platform:
        case Platform.WINDOWS:
            config_dir = "AppData/Roaming/"
        case Platform.LINUX:
            config_dir = ".config/"
        case _:
            raise NotImplementedError(f"Unsupported platform: {platform}")

    match key.category:
        case KeyCategory.DIRECTORY:
            return config_dir + key.src
        case KeyCategory.FILE:
            if key.attribute.root:
                return key.src.removesuffix(".template")
            return config_dir + key.src.removesuffix(".template")


def get_default_policy(key: EntryKey) -> Policy:
    """Resolve and return the default file synchronization policy for the given entry key.

    For directory and static file, the default policy is SYMLINK.
    For dynamic file, the default policy is COPY.
    """
    match key.category:
        case KeyCategory.DIRECTORY:
            return Policy.SYMLINK
        case KeyCategory.FILE:
            if key.attribute.static:
                return Policy.SYMLINK
            return Policy.COPY
