from pathlib import Path

from recnys.frontend.task import Policy

__all__ = ["DST_PATHS", "POLICIES", "SRC_PATHS"]


_SRC_PATHS_LINUX = (
    Path(".vimrc"),
    Path(".bashrc"),
    Path(".inputrc"),
    Path(".tmux.conf"),
    Path(".gitconfig"),
    Path(".config/nvim/foo"),
    Path(".config/helix/foo"),
    Path(".config/yazi/foo"),
)
_SRC_PATHS_LINUX = tuple(Path.cwd() / p for p in _SRC_PATHS_LINUX)
_SRC_PATHS_WINDOWS = (
    Path(".vimrc"),
    None,
    None,
    None,
    Path(".gitconfig"),
    Path(".config/nvim/foo"),
    Path(".config/helix/foo"),
    Path(".config/yazi/foo"),
)
_SRC_PATHS_WINDOWS = tuple(Path.cwd() / p for p in _SRC_PATHS_WINDOWS if p is not None)
SRC_PATHS = {"Linux": _SRC_PATHS_LINUX, "Windows": _SRC_PATHS_WINDOWS}

_DST_PATHS_LINUX = (
    Path("~/.vimrc"),
    Path("~/.bashrc"),
    Path("~/.inputrc"),
    Path("~/.tmux.conf"),
    Path("~/.gitconfig"),
    Path("~/.config/nvim/foo"),
    Path("~/.config/helix/foo"),
    Path("~/.config/yazi/foo"),
)
_DST_PATHS_LINUX = tuple(p.expanduser() for p in _DST_PATHS_LINUX)

_DST_PATHS_WINDOWS = (
    Path("~/_vimrc"),
    None,
    None,
    None,
    Path("~/.gitconfig"),
    Path("~/AppData/Local/nvim/foo"),
    Path("~/AppData/Roaming/helix/foo"),
    Path("~/AppData/Roaming/yazi/foo"),
)
_DST_PATHS_WINDOWS = tuple(p.expanduser() for p in _DST_PATHS_WINDOWS if p is not None)
DST_PATHS = {
    "Linux": _DST_PATHS_LINUX,
    "Windows": _DST_PATHS_WINDOWS,
}

_POLICIES_LINUX = [Policy.OVERWRITE] * len(_SRC_PATHS_LINUX)
_POLICIES_LINUX[1] = Policy.SOURCE
_POLICIES_WINDOWS = [Policy.OVERWRITE] * len(_SRC_PATHS_WINDOWS)
POLICIES = {"Linux": _POLICIES_LINUX, "Windows": _POLICIES_WINDOWS}
