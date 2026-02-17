"""Provide `CanonicalConfig` and related data structures.

`CanonicalConfig` is the central data structure that modules in this project
communicate with.
"""

from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

from recnys.sync.task import FileSyncPolicy

__all__ = ["CanonicalConfig", "CanonicalConfigValue", "RenderSpec", "SyncSpec"]


type CanonicalConfig = dict[str, CanonicalConfigValue]


class RenderSpec(NamedTuple):
    src: Path
    dst: Path | None


class SyncSpec(NamedTuple):
    src: Path
    dst: Path | None
    policy: FileSyncPolicy


class CanonicalConfigValue(NamedTuple):
    sync_spec: SyncSpec
    render_spec: RenderSpec
