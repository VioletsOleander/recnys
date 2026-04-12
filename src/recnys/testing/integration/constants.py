from functools import cached_property
from pathlib import Path

__all__ = ["CTREE_FNAME", "DTREE_FNAME", "RECNYS_FNAME", "VARIABLES_FNAME", "LazyConstants"]

RECNYS_FNAME = "recnys.yaml"
VARIABLES_FNAME = "variables.yaml"
CTREE_FNAME = "prev_ctree.json"
DTREE_FNAME = "prev_dtree.json"


class _LazyConstants:
    @cached_property
    def cwd(self) -> Path:
        """Current working directory."""
        return Path.home() / "repo"

    @cached_property
    def data_dir(self) -> Path:
        """Data directory path."""
        return self.cwd / ".recnys"

    @cached_property
    def recnys_file(self) -> Path:
        """Path to the recnys.yaml file."""
        return self.cwd / RECNYS_FNAME

    @cached_property
    def variables_file(self) -> Path:
        """Path to the variables.yaml file."""
        return self.cwd / VARIABLES_FNAME

    @cached_property
    def ctree_file(self) -> Path:
        """Path to the prev_ctree.json file."""
        return self.data_dir / CTREE_FNAME

    @cached_property
    def dtree_file(self) -> Path:
        """Path to the prev_dtree.json file."""
        return self.data_dir / DTREE_FNAME

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
