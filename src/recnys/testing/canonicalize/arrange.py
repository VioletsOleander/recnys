from pathlib import Path
from typing import TYPE_CHECKING

from recnys.canonicalize.canonicalizer import ConfigCanonicalizer
from recnys.canonicalize.config import CanonicalConfigValue, RenderSpec, SyncSpec
from recnys.sync.task import FileSyncPolicy

from .constants import LazyConstants

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.canonicalize.config import CanonicalConfig

__all__ = ["create_source_files", "make_canonical_config", "make_canonicalizer"]


def create_source_files(filesystem: FakeFilesystem) -> None:
    """Create the source files in the fake filesystem."""
    for f in LazyConstants.files_to_create:
        filesystem.create_file(file_path=f)


def make_canonicalizer() -> ConfigCanonicalizer:
    """Construct and return a ConfigCanonicalizer.

    This function should be called after the fake filesystem is set up.
    """
    return ConfigCanonicalizer(rendered_file_dir=LazyConstants.rendered_file_dir)


def make_canonical_config(system: str) -> CanonicalConfig:
    """Construct and return the expected CanonicalConfig.

    The function should be called after the fake filesystem is set up.
    """
    match system:
        case "Windows":
            return {
                ".vimrc": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / ".vimrc",
                        dst=Path.home() / "_vimrc",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / ".vimrc", dst=None),
                ),
                ".gitconfig": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / ".gitconfig",
                        dst=Path.home() / ".gitconfig",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / ".gitconfig", dst=None),
                ),
                ".bashrc.template": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=LazyConstants.rendered_file_dir / ".bashrc",
                        dst=None,
                        policy=FileSyncPolicy.SOURCE,
                    ),
                    render_spec=RenderSpec(
                        src=Path.cwd() / ".bashrc.template",
                        dst=None,
                    ),
                ),
                "nvim/init.lua": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nvim/init.lua",
                        dst=Path.home() / "AppData/Local/nvim/init.lua",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nvim/init.lua", dst=None),
                ),
                "nvim/lua/config/lazy.lua": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nvim/lua/config/lazy.lua",
                        dst=Path.home() / "AppData/Local/nvim/lua/config/lazy.lua",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nvim/lua/config/lazy.lua", dst=None),
                ),
                "yazi/yazi.toml": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "yazi/yazi.toml",
                        dst=Path.home() / "AppData/Roaming/yazi/yazi.toml",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "yazi/yazi.toml", dst=None),
                ),
                "nushell/config.nu.template": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=LazyConstants.rendered_file_dir / "nushell/config.nu",
                        dst=Path.home() / "AppData/Roaming/nushell/config.nu",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(
                        src=Path.cwd() / "nushell/config.nu.template",
                        dst=LazyConstants.rendered_file_dir / "nushell/config.nu",
                    ),
                ),
                "nushell/env.nu": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nushell/env.nu",
                        dst=Path.home() / "AppData/Roaming/nushell/env.nu",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nushell/env.nu", dst=None),
                ),
            }
        case "Linux":
            return {
                ".vimrc": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / ".vimrc",
                        dst=Path.home() / ".vimrc",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / ".vimrc", dst=None),
                ),
                ".gitconfig": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / ".gitconfig",
                        dst=Path.home() / ".gitconfig",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / ".gitconfig", dst=None),
                ),
                ".bashrc.template": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=LazyConstants.rendered_file_dir / ".bashrc",
                        dst=Path.home() / ".bashrc",
                        policy=FileSyncPolicy.SOURCE,
                    ),
                    render_spec=RenderSpec(
                        src=Path.cwd() / ".bashrc.template",
                        dst=LazyConstants.rendered_file_dir / ".bashrc",
                    ),
                ),
                "nvim/init.lua": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nvim/init.lua",
                        dst=Path.home() / ".config/nvim/init.lua",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nvim/init.lua", dst=None),
                ),
                "nvim/lua/config/lazy.lua": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nvim/lua/config/lazy.lua",
                        dst=Path.home() / ".config/nvim/lua/config/lazy.lua",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nvim/lua/config/lazy.lua", dst=None),
                ),
                "yazi/yazi.toml": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "yazi/yazi.toml",
                        dst=Path.home() / ".config/yazi/yazi.toml",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "yazi/yazi.toml", dst=None),
                ),
                "nushell/config.nu.template": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=LazyConstants.rendered_file_dir / "nushell/config.nu",
                        dst=Path.home() / ".config/nushell/config.nu",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(
                        src=Path.cwd() / "nushell/config.nu.template",
                        dst=LazyConstants.rendered_file_dir / "nushell/config.nu",
                    ),
                ),
                "nushell/env.nu": CanonicalConfigValue(
                    sync_spec=SyncSpec(
                        src=Path.cwd() / "nushell/env.nu",
                        dst=Path.home() / ".config/nushell/env.nu",
                        policy=FileSyncPolicy.COPY,
                    ),
                    render_spec=RenderSpec(src=Path.cwd() / "nushell/env.nu", dst=None),
                ),
            }
        case _:
            raise NotImplementedError(f"Unsupported OS: {system}")
