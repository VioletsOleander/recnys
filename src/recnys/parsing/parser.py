"""Provide `ConfigParser`."""

import logging
from typing import TYPE_CHECKING

from recnys.utils.platform import Platform

from .deconflict import deconflict
from .defaulting import get_default_dest, get_default_policy
from .model import EntryKey, EntryValue, KeyAttribute, KeyCategory, ParsedConfig

if TYPE_CHECKING:
    from collections.abc import Iterable

    from recnys.scanning.model import EntryValue as ScannedEntryValue
    from recnys.scanning.model import ScannedConfig

__all__ = ["ConfigParser"]

logger = logging.getLogger(__name__)


class ConfigParser:
    """ConfigParser transforms the scanned configuration into a parsed form."""

    _platform: Platform

    def __init__(self, platform: Platform) -> None:
        self._platform = platform

    def parse(self, scanned_config: ScannedConfig) -> ParsedConfig:
        """Transform the scanned configuration into a parsed form.

        Parsing does not involve any filesystem IO operations, and only relies on the scanned
        configuration and the platform information.

        Parsing includes:
        - Transform scanned entry keys into EntryKey instances, with deconfliction for dropping
            entries and detecting unsupported conflicts.
        - Transform scanned entry values into EntryValue instances, defaulting missing fields, dropping
            entries with empty destination.

        Args:
            scanned_config (ScannedConfig): The scanned configuration to be parsed.

        Returns:
            ParsedConfig: The parsed configuration.
        """
        logger.debug("Parsing configuration")
        config = scanned_config.root
        parsed_config: dict[EntryKey, EntryValue] = {}

        keys = self._parse_keys(keys=config.keys())
        for key in keys:
            value = self._parse_value(key=key, value=config[key.src])
            if value is not None:
                parsed_config[key] = value

        logger.debug("Parsed configuration: %s", parsed_config)
        return ParsedConfig(parsed_config)

    def _parse_keys(self, keys: Iterable[str]) -> list[EntryKey]:
        """Return parsed entry keys."""

        def build_entry_key(key: str) -> EntryKey:
            category = KeyCategory.DIRECTORY if key.endswith("/") else KeyCategory.FILE

            static = not key.endswith(".template")
            root = "/" not in key.removesuffix("/")

            return EntryKey(
                src=key, category=category, attribute=KeyAttribute(static=static, root=root)
            )

        return deconflict(keys=map(build_entry_key, keys))

    def _parse_value(self, key: EntryKey, value: ScannedEntryValue | None) -> EntryValue | None:
        """Return parsed entry value or None if the entry should be dropped."""
        if value is None:
            dest = get_default_dest(key=key, platform=self._platform)
            policy = get_default_policy(key=key)
            return EntryValue(dest=dest, policy=policy)

        if value.dest is None:
            dest = get_default_dest(key=key, platform=self._platform)
        else:
            dest = value.dest.Linux if self._platform == Platform.LINUX else value.dest.Windows
            dest = get_default_dest(key=key, platform=self._platform) if dest is None else dest

        if dest == "":
            return None

        policy = get_default_policy(key=key) if value.policy is None else value.policy

        return EntryValue(dest=dest, policy=policy)
