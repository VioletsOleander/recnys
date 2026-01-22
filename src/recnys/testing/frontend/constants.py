__all__ = ["CONFIG_FILE_CONTENT", "LOADED_CONFIG"]

CONFIG_FILE_CONTENT = r"""{
    ".vimrc": { dest: { windows: "_vimrc" } },
    ".bashrc": { dest: { windows: "" }, policy: "source" },
    ".gitconfig",
    "nvim/": { dest: { windows: "AppData/Local/nvim" } },
    "yazi/",
}
"""

LOADED_CONFIG = {
    ".vimrc": {"dest": {"windows": "_vimrc"}},
    ".bashrc": {"dest": {"windows": ""}, "policy": "source"},
    ".gitconfig": None,
    "nvim/": {"dest": {"windows": "AppData/Local/nvim"}},
    "yazi/": None,
}
