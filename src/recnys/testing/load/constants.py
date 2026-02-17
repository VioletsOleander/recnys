from __future__ import annotations

from functools import cached_property
from pathlib import Path

from recnys.load import LoadedConfig, LoadedVariables

__all__ = [
    "CONFIG_FILE_CONTENT",
    "CONFIG_FILE_NAME",
    "LOADED_CONFIG",
    "LOADED_VARIABLES",
    "VARIABLES_FILE_CONTENT",
    "VARIABLES_FILE_NAME",
    "LazyConstants",
]

CONFIG_FILE_NAME = "recnys.yaml"

CONFIG_FILE_CONTENT = r"""{
    ".vimrc": { dest: { Windows: "_vimrc" } },
    ".bashrc.template": { dest: { Windows: "" }, policy: "source"},
    ".gitconfig",
    "nvim/": { dest: { Windows: "AppData/Local/nvim" } },
    "yazi/",
    "nushell/",
    "nushell/config.nu.template",
}
"""

VARIABLES_FILE_NAME = "variables.yaml"

VARIABLES_FILE_CONTENT = r"""{ proxy_url: "http://proxy.example.com:8080" }"""

LOADED_CONFIG: LoadedConfig = {
    ".vimrc": {"dest": {"Windows": "_vimrc"}},
    ".bashrc.template": {"dest": {"Windows": ""}, "policy": "source"},
    ".gitconfig": None,
    "nvim/": {"dest": {"Windows": "AppData/Local/nvim"}},
    "yazi/": None,
    "nushell/": None,
    "nushell/config.nu.template": None,
}

LOADED_VARIABLES: LoadedVariables = {"proxy_url": "http://proxy.example.com:8080"}


class _LazyConstants:
    @cached_property
    def config_file_path(self) -> Path:
        return Path.cwd() / CONFIG_FILE_NAME

    @cached_property
    def variables_file_path(self) -> Path:
        return Path.cwd() / VARIABLES_FILE_NAME


LazyConstants = _LazyConstants()
