from typing import TYPE_CHECKING

from .render.task import TemplateRenderTask
from .sync.task import FileSyncTask

if TYPE_CHECKING:
    from .canonicalize.config import CanonicalConfig

__all__ = ["build_render_tasks", "build_sync_tasks"]


def build_sync_tasks(config: CanonicalConfig, *, force_execute: bool = False) -> list[FileSyncTask]:
    """Build file synchronization tasks from the canonical configuration."""
    return [
        FileSyncTask(
            src=value.sync_spec.src,
            dst=value.sync_spec.dst,
            policy=value.sync_spec.policy,
            force_execute=force_execute,
        )
        for value in config.values()
        if value.sync_spec.dst is not None
    ]


def build_render_tasks(
    config: CanonicalConfig, *, force_execute: bool = False
) -> list[TemplateRenderTask]:
    """Build template rendering tasks from the canonical configuration."""
    return [
        TemplateRenderTask(
            src=value.render_spec.src,
            dst=value.render_spec.dst,
            force_execute=force_execute,
        )
        for value in config.values()
        if value.render_spec.dst is not None
    ]
