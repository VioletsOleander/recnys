from recnys.frontend.task import Policy

__all__ = [
    "CONFIG_FILE_CONTENT",
    "DEST_FILES_LINUX",
    "DEST_FILES_WINDOWS",
    "POLICIES_LINUX",
    "POLICIES_WINDOWS",
    "SOURCE_FILES_LINUX",
    "SOURCE_FILES_WINDOWS",
]

CONFIG_FILE_CONTENT = r"""{
    ".vimrc": { dest: { windows: "_vimrc" } },
    ".bashrc": { dest: { windows: "" }, policy: "source" },
    ".gitconfig",
    "nvim/": { dest: { windows: "AppData/Local/nvim" } },
    "yazi/",
}
"""

SOURCE_FILES_LINUX = (
    ".vimrc",
    ".bashrc",
    ".gitconfig",
    "nvim/init.lua",
    "nvim/lua/config/lazy.lua",
    "nvim/lua/plugins/treesitter.lua",
    "yazi/yazi.toml",
)


DEST_FILES_LINUX = (
    ".vimrc",
    ".bashrc",
    ".gitconfig",
    ".config/nvim/init.lua",
    ".config/nvim/lua/config/lazy.lua",
    ".config/nvim/lua/plugins/treesitter.lua",
    ".config/yazi/yazi.toml",
)

POLICIES_LINUX = (
    Policy.OVERWRITE,
    Policy.SOURCE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
)

SOURCE_FILES_WINDOWS = (
    ".vimrc",
    ".gitconfig",
    "nvim/init.lua",
    "nvim/lua/config/lazy.lua",
    "nvim/lua/plugins/treesitter.lua",
    "yazi/yazi.toml",
)


DEST_FILES_WINDOWS = (
    "_vimrc",
    ".gitconfig",
    "AppData/Local/nvim/init.lua",
    "AppData/Local/nvim/lua/config/lazy.lua",
    "AppData/Local/nvim/lua/plugins/treesitter.lua",
    "AppData/Roaming/yazi/yazi.toml",
)


POLICIES_WINDOWS = (
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
    Policy.OVERWRITE,
)
