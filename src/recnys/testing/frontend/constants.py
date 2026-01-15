from pathlib import Path

from recnys.frontend.task import Policy

__all__ = ["DST_PARAMS", "POLICIES", "SRC_PARAMS"]

_SRC_PARAMS = (
    (Path(".vimrc"), False),
    (Path(".bashrc"), False),
    (Path(".inputrc"), False),
    (Path(".tmux.conf"), False),
    (Path(".gitconfig"), False),
    (Path(".config/nvim/"), True),
    (Path(".config/helix/"), True),
    (Path(".config/yazi/"), True),
)
SRC_PARAMS = tuple((Path.cwd() / p, is_dir) for p, is_dir in _SRC_PARAMS)

_DST_PARAMS_LINUX = (Path.home() / p for p, _ in _SRC_PARAMS)
_DST_PARAMS_LINUX = tuple(p.expanduser() for p in _DST_PARAMS_LINUX)

_DST_PARAMS_WINDOWS = (
    Path("~/_vimrc"),
    None,
    None,
    None,
    Path("~/.gitconfig"),
    Path("~/AppData/Local/nvim"),
    Path("~/AppData/Roaming/helix"),
    Path("~/AppData/Roaming/yazi"),
)
_DST_PARAMS_WINDOWS = tuple(p.expanduser() if p is not None else None for p in _DST_PARAMS_WINDOWS)
DST_PARAMS = {
    "Linux": _DST_PARAMS_LINUX,
    "Windows": _DST_PARAMS_WINDOWS,
}

_POLICIES = [Policy.OVERWRITE] * len(SRC_PARAMS)
_POLICIES[1] = Policy.SOURCE
POLICIES = tuple(_POLICIES)
