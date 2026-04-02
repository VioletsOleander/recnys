"""Provide `ConfigCanonicalizer`."""

from pathlib import Path
from typing import TYPE_CHECKING

from recnys.sync.task import FileSyncPolicy

from .deconflict import deconflict
from .model import CanonicalConfig, EntryKey, EntryValue, KeyCategory

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

    from recnys.config.model import EntryValue as PrimitiveEntryValue
    from recnys.config.model import LoadedConfig
    from recnys.utils.platform import Platform

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
            if key.endswith("/"):
                category = KeyCategory.DIRECTORY
            elif key.endswith(".template"):
                category = KeyCategory.DYNAMIC_FILE
            else:
                category = KeyCategory.STATIC_FILE
            return EntryKey(src=key, category=category)

        return deconflict(keys=map(build_entry_key, keys))

    def _canonicalize_value(
        self, key: EntryKey, value: PrimitiveEntryValue | None
    ) -> EntryValue | None:
        """Return canonicalized entry value or None if the entry should be dropped."""
    def _resolve_dst(self, key: str, value: ConfigValue) -> Path | None:
        """Return None if the destination is specified as an empty string, which means no syncing."""
        default_dst = self._resolve_default_dst(key)
        if value is None:
            return default_dst

        match value.get("dest"):
            case None:
                return default_dst
            case dict() as sync_dsts:
                match sync_dsts.get(self._system.value):
                    case "":
                        return None
                    case str() as dst:
                        return Path.home() / Path(dst)
                    case None:
                        return default_dst
                    case _ as val:
                        raise ValueError(
                            f"Invalid destination value for {self._system.value}: {val}."
                            " It should be either an empty string or a string path."
                        )
            case _ as val:
                raise ValueError(
                    f"Invalid destination value for {self._system.value}: {val}."
                    " It should be either an empty string, a string path, or None."
                )

    def _resolve_policy(self, value: ConfigValue) -> FileSyncPolicy:
        if value is None:
            return FileSyncPolicy.DEFAULT

        match value.get("policy"):
            case None:
                return FileSyncPolicy.DEFAULT
            case "copy":
                return FileSyncPolicy.COPY
            case "source":
                return FileSyncPolicy.SOURCE
            case _ as val:
                raise ValueError(
                    f"Invalid policy value: {val}. The valid options are 'copy' or 'source'."
                )
