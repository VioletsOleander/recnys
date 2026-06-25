from recnys.testing.constants import NORMAL_CONTENT, RENDERED_CONTENT, TEMPLATE_CONTENT
from recnys.testing.node import File, Symlink

__all__ = ["LINUX_TARGETS", "SOURCES", "WINDOWS_TARGETS"]

SOURCES = (
    File(path=".bashrc.template", content=TEMPLATE_CONTENT),
    File(path="nushell/config.nu", content=NORMAL_CONTENT),
    File(path="nushell/autoload/commands/net.nu.template", content=TEMPLATE_CONTENT),
    File(path="nushell/autoload/commands.nu", content=NORMAL_CONTENT),
    File(path="nvim/init.lua", content=NORMAL_CONTENT),
    File(path="nvim/after/ftplugin/gitcommit.lua", content=NORMAL_CONTENT),
    File(path="nvim/after/ftplugin/python.lua", content=NORMAL_CONTENT),
    File(path="nvim/lua/config/keymap.lua", content=NORMAL_CONTENT),
    File(path="nvim/lua/plugins/pick.lua", content=NORMAL_CONTENT),
    File(path=".gitconfig", content=NORMAL_CONTENT),
)

WINDOWS_TARGETS = (
    Symlink(src="nushell/config.nu", dst="AppData/Roaming/nushell/config.nu"),
    Symlink(src="nushell/autoload/commands.nu", dst="AppData/Roaming/nushell/autoload/commands.nu"),
    File(path="AppData/Roaming/nushell/autoload/commands/net.nu", content=RENDERED_CONTENT),
    Symlink(src="nvim/", dst="AppData/Local/nvim/"),
    Symlink(src=".gitconfig", dst=".gitconfig"),
)

LINUX_TARGETS = (
    File(path="my_bashrc", content=RENDERED_CONTENT),
    Symlink(src="nushell/config.nu", dst=".config/nushell/config.nu"),
    Symlink(src="nushell/autoload/commands.nu", dst=".config/nushell/autoload/commands.nu"),
    File(path=".config/nushell/autoload/commands/net.nu", content=RENDERED_CONTENT),
    Symlink(src="nvim/", dst=".config/nvim/"),
    Symlink(src=".gitconfig", dst=".gitconfig"),
)
