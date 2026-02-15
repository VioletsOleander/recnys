from pathlib import Path

from recnys.render.task import TemplateRenderTask
from recnys.sync.task import FileSyncPolicy, FileSyncTask
from recnys.testing.canonicalize.constants import LazyConstants

__all__ = ["make_sync_tasks"]


def make_sync_tasks(system: str) -> list[FileSyncTask]:
    """Construct and return the expected list of FileSyncTask.

    This function should be called after the fake filesystem is set up.
    """
    match system:
        case "Windows":
            return [
                FileSyncTask(
                    src=Path.cwd() / ".vimrc",
                    dst=Path.home() / "_vimrc",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / ".gitconfig",
                    dst=Path.home() / ".gitconfig",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nvim/init.lua",
                    dst=Path.home() / "AppData/Local/nvim/init.lua",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nvim/lua/config/lazy.lua",
                    dst=Path.home() / "AppData/Local/nvim/lua/config/lazy.lua",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "yazi/yazi.toml",
                    dst=Path.home() / "AppData/Roaming/yazi/yazi.toml",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=LazyConstants.rendered_file_dir / "nushell/config.nu",
                    dst=Path.home() / "AppData/Roaming/nushell/config.nu",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nushell/env.nu",
                    dst=Path.home() / "AppData/Roaming/nushell/env.nu",
                    policy=FileSyncPolicy.COPY,
                ),
            ]
        case "Linux":
            return [
                FileSyncTask(
                    src=Path.cwd() / ".vimrc",
                    dst=Path.home() / ".vimrc",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / ".gitconfig",
                    dst=Path.home() / ".gitconfig",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=LazyConstants.rendered_file_dir / ".bashrc",
                    dst=Path.home() / ".bashrc",
                    policy=FileSyncPolicy.SOURCE,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nvim/init.lua",
                    dst=Path.home() / ".config/nvim/init.lua",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nvim/lua/config/lazy.lua",
                    dst=Path.home() / ".config/nvim/lua/config/lazy.lua",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "yazi/yazi.toml",
                    dst=Path.home() / ".config/yazi/yazi.toml",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=LazyConstants.rendered_file_dir / "nushell/config.nu",
                    dst=Path.home() / ".config/nushell/config.nu",
                    policy=FileSyncPolicy.COPY,
                ),
                FileSyncTask(
                    src=Path.cwd() / "nushell/env.nu",
                    dst=Path.home() / ".config/nushell/env.nu",
                    policy=FileSyncPolicy.COPY,
                ),
            ]
        case _:
            raise NotImplementedError(f"Unsupported system: {system}")


def make_render_tasks(system: str) -> list[TemplateRenderTask]:
    """Construct and return the expected list of TemplateRenderTask.

    This function should be called after the fake filesystem is set up.
    """
    match system:
        case "Windows":
            return [
                TemplateRenderTask(
                    src=Path.cwd() / "nushell/config.nu.template",
                    dst=LazyConstants.rendered_file_dir / "nushell/config.nu",
                ),
            ]
        case "Linux":
            return [
                TemplateRenderTask(
                    src=Path.cwd() / ".bashrc.template",
                    dst=LazyConstants.rendered_file_dir / ".bashrc",
                ),
                TemplateRenderTask(
                    src=Path.cwd() / "nushell/config.nu.template",
                    dst=LazyConstants.rendered_file_dir / "nushell/config.nu",
                ),
            ]
        case _:
            raise NotImplementedError(f"Unsupported system: {system}")
