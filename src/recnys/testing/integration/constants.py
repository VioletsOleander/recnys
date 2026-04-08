from functools import cached_property
from pathlib import Path

__all__ = [
    "RECNYS_FCONTENT",
    "RECNYS_FNAME",
    "VARIABLES_FCONTENT",
    "VARIABLES_FNAME",
    "LazyConstants",
]

RECNYS_FNAME = "recnys.yaml"

RECNYS_FCONTENT = r"""
{
    ".vimrc": { dest: { Windows: "_vimrc", Linux: ".vimrc" } },
    ".bashrc.template": { dest: { Windows: "", Linux: "my_bashrc" } },
    ".gitconfig": { dest: { Windows: ".gitconfig", Linux: ".gitconfig" } },
    "nvim/": { dest: { Windows: "AppData/Local/nvim" }, policy: "copy" },
    "yazi/config/",
    "nushell/",
    "nushell/autoload/net.nu.template",
}
"""

VARIABLES_FNAME = "variables.yaml"

VARIABLES_FCONTENT = r"""{ proxy_url: "http://proxy.example.com:8080" }"""


class _LazyConstants:
    @cached_property
    def cwd(self) -> Path:
        """Current working directory."""
        return (Path.home() / "repo").absolute()

    @cached_property
    def recnys_file(self) -> Path:
        """Path to the recnys.yaml file."""
        return self.cwd / RECNYS_FNAME

    @cached_property
    def variables_file(self) -> Path:
        """Path to the variables.yaml file."""
        return self.cwd / VARIABLES_FNAME

    @cached_property
    def files_to_create(self) -> tuple[Path, ...]:
        cwd = self.cwd
        return (
            cwd / ".vimrc",
            cwd / ".bashrc.template",
            cwd / ".gitconfig",
            cwd / "nvim/init.lua",
            cwd / "nvim/after/ftplugin/gitcommit.lua",
            cwd / "nvim/after/ftplugin/python.lua",
            cwd / "nvim/lua/config/keymap.lua",
            cwd / "nvim/lua/plugins/edit.lua",
            cwd / "yazi/config/yazi.toml",
            cwd / "nushell/config.nu",
            cwd / "nushell/autoload/net.nu.template",
            cwd / "nushell/autoload/zoxide.nu",
        )


LazyConstants = _LazyConstants()
