"""Provide `ConfigCanonicalizer`."""

from typing import TYPE_CHECKING

from recnys.utils.platform import Platform

from .deconflict import deconflict
from .defaulting import get_default_dest, get_default_policy
from .model import CanonicalConfig, EntryKey, EntryValue, KeyAttribute, KeyCategory

if TYPE_CHECKING:
    from collections.abc import Iterable

    from recnys.config.model import EntryValue as PrimitiveEntryValue
    from recnys.config.model import LoadedConfig

__all__ = ["ConfigCanonicalizer"]


class ConfigCanonicalizer:
    """ConfigCanonicalizer transforms the loaded configuration into a canonical form.

    The main provided method is `canonicalize`.
    """

    _platform: Platform

    def __init__(self, platform: Platform) -> None:
        self._platform = platform

    def canonicalize(self, loaded_config: LoadedConfig) -> CanonicalConfig:
        """Transform the loaded configuration into a canonical form.

        Canonicalization does not involve any filesystem IO operations, and only relies on the loaded
        configuration and the platform information.

        Canonicalization includes:
        - Transform primitive entry keys into EntryKey instances, with deconfliction for dropping
            entries and populating information for later special handling.
        - Transform primitive entry values into EntryValue instances, defaulting missing fields, dropping
            entries with empty destination.

        Entries included in the canonical configuration are the effective entries for instructing
        actual execution.

        Args:
            loaded_config (LoadedConfig): The loaded configuration to be canonicalized.

        Returns:
            CanonicalConfig: The canonicalized configuration.
        """
        config = loaded_config.root
        canonical_config: dict[EntryKey, EntryValue] = {}

        keys = self._canonicalize_keys(keys=config.keys())
        for key in keys:
            value = self._canonicalize_value(key=key, value=config[key.src])
            if value is not None:
                canonical_config[key] = value

        return CanonicalConfig(canonical_config)

    def _canonicalize_keys(self, keys: Iterable[str]) -> list[EntryKey]:
        """Return canonicalized entry keys."""

        def build_entry_key(key: str) -> EntryKey:
            category = KeyCategory.DIRECTORY if key.endswith("/") else KeyCategory.FILE

            static = not key.endswith(".template")
            root = "/" not in key.removesuffix("/")

            return EntryKey(
                src=key, category=category, attribute=KeyAttribute(static=static, root=root)
            )

        return deconflict(keys=map(build_entry_key, keys))

    def _canonicalize_value(
        self, key: EntryKey, value: PrimitiveEntryValue | None
    ) -> EntryValue | None:
        """Return canonicalized entry value or None if the entry should be dropped."""
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
