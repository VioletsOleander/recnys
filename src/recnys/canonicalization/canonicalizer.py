"""Provide `ConfigCanonicalizer`."""

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from recnys.parsing.model import KeyCategory as ParsedKeyCategory
from recnys.scanning.model import Policy

from .model import CanonicalizedConfig, EntryKey, EntryValue

if TYPE_CHECKING:
    from collections.abc import Generator

    from recnys.parsing.model import ParsedConfig


__all__ = ["ConfigCanonicalizer"]

logger = logging.getLogger(__name__)


class ConfigCanonicalizer:
    """ConfigCanonicalizer transforms the parsed configuration into a canonical form."""

    _home: Path
    _repo_dir: Path

    def __init__(self, home: Path, repo_dir: Path) -> None:
        """Initialize the ConfigCanonicalizer.

        Args:
            home (Path): The home directory path.
            repo_dir (Path): The repository root directory path.
        """
        self._home = home
        self._repo_dir = repo_dir

    def canonicalize(self, parsed_config: ParsedConfig) -> CanonicalizedConfig:
        """Transform the parsed configuration into a canonical form.

        Canonicalization involves:

        - Constructing absolute src and dest paths.
        - Expanding directory entries with COPY policy into individual file entries.

        Args:
            parsed_config (ParsedConfig): The parsed configuration to be canonicalized.

        Returns:
            CanonicalizedConfig: The canonicalized configuration.
        """
        logger.debug("Canonicalizing configuration")
        config = parsed_config.root
        canonicalized_config: dict[EntryKey, EntryValue] = {}

        for key, value in config.items():
            if key.category == ParsedKeyCategory.DIRECTORY and value.policy == Policy.COPY:
                file_paths = self._expand_directory(base_dir=key.src, exclude_dirs=[".git"])

                for file_path in file_paths:
                    canonical_key = EntryKey(
                        src=self._repo_dir / file_path, static=file_path.suffix != ".template"
                    )
                    canonical_value = EntryValue(dest=self._home / file_path, policy=value.policy)
                    canonicalized_config[canonical_key] = canonical_value
            else:
                canonical_key = EntryKey(src=self._repo_dir / key.src, static=key.attribute.static)
                canonical_value = EntryValue(dest=self._home / value.dest, policy=value.policy)
                canonicalized_config[canonical_key] = canonical_value

        logger.debug("Canonicalized configuration: %s", canonicalized_config)
        return CanonicalizedConfig(canonicalized_config)

    def _expand_directory(self, base_dir: str, exclude_dirs: list[str]) -> Generator[Path]:
        """Generate individual file paths by expanding the given directory path.

        Args:
            base_dir (str): The directory path to be expanded.
            exclude_dirs (list[str]): The list of directory names to be excluded from expansion.

        Yields:
            Path: Individual file paths within the expanded directory, relative to the parent
                directory of base_dir.
        """
        for dir_path, dir_names, file_names in Path(base_dir).walk():
            for name in exclude_dirs:
                if name in dir_names:
                    dir_names.remove(name)

            for file_name in file_names:
                yield Path(dir_path) / file_name
