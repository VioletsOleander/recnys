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

        Args:
            loaded_config (LoadedConfig): The loaded configuration to be canonicalized.

        Returns:
            CanonicalConfig: The canonicalized configuration.
        """
        config = loaded_config.root

        keys = self._canonicalize_keys(keys=config.keys())
        keys = deconflict(keys=keys)

        raise KeyboardInterrupt

        for key, value in config.items():
            sync_spec = self._make_sync_spec(key=key, value=value)

            if key.endswith("/"):
                expanded_sync_specs = self._expand_directory(sync_spec=sync_spec)
                sync_specs.update(expanded_sync_specs)
            else:
                sync_specs[key] = sync_spec

        return canonical_config

    def _canonicalize_keys(self, keys: Iterable[str]) -> Generator[EntryKey]:
        """Generate EntryKey instances from the source paths specified in the configuration file."""
        for src in keys:
            if src.endswith("/"):
                category = KeyCategory.DIRECTORY
            elif src.endswith(".template"):
                category = KeyCategory.DYNAMIC_FILE
            else:
                category = KeyCategory.STATIC_FILE

            yield EntryKey(src=src, category=category)

    def _expand_directory(self, sync_spec: SyncSpec) -> dict[str, SyncSpec]:
        result: dict[str, SyncSpec] = {}

        src_dir = sync_spec.src
        dst_dir = sync_spec.dst
        for src_file in src_dir.rglob("*"):
            if not src_file.is_file():
                continue

            key = src_file.relative_to(Path.cwd()).as_posix()
            src = self._resolve_src(key)

            if dst_dir is None:
                dst = None
            else:
                dst = dst_dir / src_file.relative_to(src_dir)
                if dst.suffix.endswith(".template"):
                    dst = dst.with_suffix("")

            file_sync_spec = SyncSpec(src=src, dst=dst, policy=sync_spec.policy)

            result[key] = file_sync_spec

        return result

    def _make_sync_spec(self, key: str, value: ConfigValue) -> SyncSpec:
        src = self._resolve_src(key)
        dst = self._resolve_dst(key, value)
        policy = self._resolve_policy(value)

        return SyncSpec(src=src, dst=dst, policy=policy)

    def _resolve_src(self, key: str) -> Path:
        if key.endswith(".template"):
            return self._rendered_file_dir / key.removesuffix(".template")
        return Path.cwd() / key

    def _resolve_default_dst(self, key: str) -> Path:
        key = key.removesuffix(".template")

        if "/" in key:
            match self._system:
                case SupportedSystem.WINDOWS:
                    return Path.home() / "AppData/Roaming" / key
                case SupportedSystem.LINUX:
                    return Path.home() / ".config" / key

        return Path.home() / key

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
