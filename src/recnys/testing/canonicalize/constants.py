from functools import cached_property
from pathlib import Path

__all__ = ["LazyConstants"]


class _LazyConstants:
    @cached_property
    def rendered_file_dir(self) -> Path:
        return Path.cwd() / ".recnys/rendered"

    @cached_property
    def files_to_create(self) -> tuple[Path, ...]:
        return (
            Path.cwd() / ".vimrc",
            Path.cwd() / ".bashrc.template",
            Path.cwd() / ".gitconfig",
            Path.cwd() / "nvim/init.lua",
            Path.cwd() / "nvim/lua/config/lazy.lua",
            Path.cwd() / "yazi/yazi.toml",
            Path.cwd() / "nushell/config.nu.template",
            Path.cwd() / "nushell/env.nu",
        )


LazyConstants = _LazyConstants()
