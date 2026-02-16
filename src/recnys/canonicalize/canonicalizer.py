"""Provide `ConfigCanonicalizer`."""

import platform
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

from recnys.sync.task import FileSyncPolicy

from .config import CanonicalConfig, CanonicalConfigValue, RenderSpec, SyncSpec

if TYPE_CHECKING:
    from recnys.load import ConfigValue, LoadedConfig

__all__ = ["ConfigCanonicalizer", "SupportedSystem"]


class SupportedSystem(StrEnum):
    WINDOWS = "Windows"
    LINUX = "Linux"

    @classmethod
    def _missing_(cls, value: object) -> None:
        supported = ", ".join([repr(e.value) for e in cls])
        raise RuntimeError(
            f"Unsupported operating system: {value}. Currently only {supported} are supported."
        )


class ConfigCanonicalizer:
    """ConfigCanonicalizer transforms the loaded configuration into a canonical form.

    The main provided method is `canonicalize`.
    """

    _system: SupportedSystem
    _rendered_file_dir: Path

    def __init__(self, rendered_file_dir: Path) -> None:
        """Initialize the ConfigCanonicalizer.

        Args:
            rendered_file_dir (Path): The directory where rendered files will be stored.
        """
        self._rendered_file_dir = rendered_file_dir
        self._system = SupportedSystem(platform.system())

    def canonicalize(self, loaded_config: LoadedConfig) -> CanonicalConfig:
        """Transform the loaded configuration into a canonical form.

        Args:
            loaded_config (LoadedConfig): The loaded configuration to be canonicalized.

        Returns:
            CanonicalConfig: The canonicalized configuration.
        """
        sync_specs: dict[str, SyncSpec] = {}
        excluded_dirs: set[str] = set()

        # Expand directory and determine sync specifications
        for key, value in loaded_config.items():
            sync_spec = self._make_sync_spec(key=key, value=value)

            if key.endswith("/"):
                # Track directories with dst=None (excluded from syncing)
                if sync_spec.dst is None:
                    excluded_dirs.add(key.rstrip("/"))
                expanded_sync_specs = self._expand_directory(sync_spec=sync_spec)
                sync_specs.update(expanded_sync_specs)
            else:
                # Skip files under excluded directories unless they have explicit dest override
                # Files with no dest spec under excluded dirs are skipped
                # Files with explicit dest (even if empty) override parent dir exclusion
                is_under_excluded = self._is_under_excluded_dir(key, excluded_dirs)
                has_explicit_dest = value is not None and "dest" in value

                if not is_under_excluded or has_explicit_dest:
                    sync_specs[key] = sync_spec

        # Determine render specifications and construct the canonical configuration
        canonical_config: CanonicalConfig = {}
        for key, sync_spec in sync_specs.items():
            render_spec = self._make_render_spec(key=key, sync_spec=sync_spec)
            canonical_config[key] = CanonicalConfigValue(
                sync_spec=sync_spec, render_spec=render_spec
            )

        return canonical_config

    def _expand_directory(self, sync_spec: SyncSpec) -> dict[str, SyncSpec]:
        result: dict[str, SyncSpec] = {}

        src_dir = sync_spec.src
        dst_dir = sync_spec.dst
        for src_file in src_dir.rglob("*"):
            if not src_file.is_file():
                continue

            if dst_dir is None:
                dst_file = None
            else:
                dst_file = dst_dir / src_file.relative_to(src_dir)
                if dst_file.suffix.endswith(".template"):
                    dst_file = dst_file.with_suffix("")
            file_sync_spec = SyncSpec(src=src_file, dst=dst_file, policy=sync_spec.policy)
            result[src_file.relative_to(src_dir.parent).as_posix()] = file_sync_spec

        return result

    def _is_under_excluded_dir(self, file_path: str, excluded_dirs: set[str]) -> bool:
        """Check if a file path is under any excluded directory.

        Args:
            file_path (str): The file path to check.
            excluded_dirs (set[str]): Set of excluded directory paths.

        Returns:
            bool: True if the file is under an excluded directory, False otherwise.
        """
        return any(file_path.startswith(excluded_dir + "/") for excluded_dir in excluded_dirs)

    def _make_sync_spec(self, key: str, value: ConfigValue) -> SyncSpec:
        src = self._resolve_src(key)
        dst = self._resolve_dst(key, value)
        policy = self._resolve_policy(value)

        return SyncSpec(src=src, dst=dst, policy=policy)

    def _make_render_spec(self, key: str, sync_spec: SyncSpec) -> RenderSpec:
        src = Path.cwd() / key
        if not key.endswith(".template") or sync_spec.dst is None:
            dst = None
        else:
            dst = self._rendered_file_dir / key.removesuffix(".template")

        return RenderSpec(src=src, dst=dst)

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
