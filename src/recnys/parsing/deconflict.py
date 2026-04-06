"""Provide `deconflict` function for deconflicting entry keys."""

from pathlib import Path
from typing import TYPE_CHECKING

from .model import EntryKey, KeyCategory

if TYPE_CHECKING:
    from collections.abc import Iterable

__all__ = ["deconflict"]


def deconflict(keys: Iterable[EntryKey]) -> list[EntryKey]:
    """Deconflict entry keys.

    Corresponds to features/deconflict.

    Args:
        keys (Iterable[EntryKey]): The entry keys to be deconflicted.

    Returns:
        list[EntryKey]: The list of entry keys after deconfliction.
    """
    # The sequence of deconfliction is supposed to be fixed.
    keys = _deconflict_overlap(keys=keys)
    keys = _deconflict_contained(keys=keys)
    return _deconflict_container(keys=keys)


def _deconflict_overlap(keys: Iterable[EntryKey]) -> Iterable[EntryKey]:
    """Deconflict between static and dynamic files.

    Latter one wins, the lost entry will be dropped.

    Corresponds to features/deconflict:1

    Args:
        keys (Iterable[EntryKey]): The EntryKeys to be deconflicted.

    Returns:
        Iterable[EntryKey]: The remaining EntryKeys after deconfliction.
    """
    keys = list(keys)
    kept_keys: list[EntryKey] = []
    seen_fnames: set[str] = set()

    for key in reversed(keys):
        if key.category == KeyCategory.DIRECTORY:
            kept_keys.append(key)
            continue

        fname = key.src.removesuffix(".template")
        if fname not in seen_fnames:
            kept_keys.append(key)
            seen_fnames.add(fname)

    return reversed(kept_keys)


def _deconflict_contained(keys: Iterable[EntryKey]) -> Iterable[EntryKey]:
    """Deconflict between directories and their contained files/subdirectories.

    Latter one wins, the lost entry will be dropped.

    Corresponds to features/deconflict:2.2, features/deconflict:3.2

    Args:
        keys (Iterable[EntryKey]): The EntryKeys to be deconflicted.

    Returns:
        Iterable[EntryKey]: The remaining EntryKeys after deconfliction.
    """
    keys = list(keys)
    kept_keys: list[EntryKey] = []
    seen_dpaths: set[Path] = set()

    for key in reversed(keys):
        path = Path(key.src)
        if any(parent in seen_dpaths for parent in path.parents[:-1]):  # Exclude cwd "."
            continue

        kept_keys.append(key)
        if key.category == KeyCategory.DIRECTORY:
            seen_dpaths.add(path)

    return reversed(kept_keys)


def _deconflict_container(keys: Iterable[EntryKey]) -> list[EntryKey]:
    """Deconflict between directories and their contained files/subdirectories.

    Raise exception if there is such kind of conflict,
    because the behavior is undefined and we choose not to support it.

    If no conflict is found, return the input keys as a list without modification.

    Args:
        keys (Iterable[EntryKey]): The EntryKeys to be deconflicted.

    Returns:
        list[EntryKey]: Containing exactly the same keys as the input, in the same order.

    Raises:
        ValueError: If there is a conflict between a directory and its contained file/subdirectory.
    """
    keys = list(keys)
    seen_dpaths: set[Path] = set()

    path_to_key: dict[Path, EntryKey] = {Path(key.src): key for key in keys}
    for path, key in path_to_key.items():
        for parent in path.parents[:-1]:  # Exclude cwd "."
            if parent in seen_dpaths:
                raise ValueError(
                    f"Conflict found between directory '{parent}' and its contained file/subdirectory '{key.src}'"
                )

        if key.category == KeyCategory.DIRECTORY:
            seen_dpaths.add(path)

    return keys
