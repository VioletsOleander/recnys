__all__ = ["DST_CONTENT", "FILES_UNDER_DIR", "SRC_CONTENT"]

SRC_CONTENT = "Sample content for source files."
DST_CONTENT = "Sample content for destination files."

FILES_UNDER_DIR = {
    "nvim/": ("nvim/init.lua", "nvim/lua/config/lazy.lua"),
    "yazi/": ("yazi/yazi.toml",),
    "nushell/": ("nushell/config.nu", "nushell/env.nu"),
}
