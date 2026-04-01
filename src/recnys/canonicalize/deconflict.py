from typing import TYPE_CHECKING

from .model import EntryKey, KeyCategory

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable


def deconflict(keys: Iterable[EntryKey]) -> list[EntryKey]:
    keys = list(keys)
    kept_keys: list[EntryKey] = []

    # Deconflict between static and dynamic files, latter one wins -> drop lost entries
    # corresponding to features/deconflict:1
    seen_fnames: set[str] = set()
    for key in reversed(keys):
        if key.category == KeyCategory.DIRECTORY:
            kept_keys.append(key)
            continue

        fname = key.src.removesuffix(".template")
        if fname not in seen_fnames:
            kept_keys.append(key)
            seen_fnames.add(fname)

    # Deconflict between files/subdirectories and their containing directories,
    # latter one wins (container wins) -> drop lost entries
    # corresponding to features/deconflict:2.1, features/deconflict:3.1
    seen_dnames: set[str] = set()
    for key in kept_keys:
        if "/" not in key.src:
            # top-level file
            kept_keys.append(key)
        elif "/" not in key.src.rstrip("/"):
            # top-level directory
            seen_dnames.add(key.src)

    return kept_keys
