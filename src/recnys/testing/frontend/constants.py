from pathlib import Path
from typing import TYPE_CHECKING

from recnys.frontend.task import Policy

from .utils import SrcAttr, make_sync_task

if TYPE_CHECKING:
    from collections.abc import Generator

    from recnys.frontend.task import SyncTask

__all__ = ["LOADED_CONFIG", "PARSED_SYNC_TASKS"]

LOADED_CONFIG = {
    ".vimrc": {"dest": {"windows": "_vimrc"}},
    ".bashrc": {"dest": {"windows": ""}, "policy": "source"},
    ".gitconfig": None,
    "nvim/": {"dest": {"windows": "AppData/Local/nvim"}},
    "yazi/": None,
}


def _src_attrs() -> Generator[SrcAttr]:
    for sync_src in LOADED_CONFIG:
        absolute_path = Path.cwd() / sync_src
        is_dir = sync_src.endswith("/")
        yield SrcAttr(path=absolute_path, is_dir=is_dir)


def _make_default_dst(sync_src: str, system: str) -> Path:
    src_is_dir = sync_src.endswith("/")
    default_config_dir = {
        "Windows": "AppData/Roaming",
        "Linux": ".config",
    }
    dst_dir = Path.home() / default_config_dir[system] if src_is_dir else Path.home()
    return dst_dir / sync_src


def _dst_paths(system: str) -> Generator[Path | None]:
    if system not in ("Windows", "Linux"):
        raise NotImplementedError(f"Unsupported OS: {system}")

    for sync_src, sync_rule in LOADED_CONFIG.items():
        match sync_rule:
            case None:
                yield _make_default_dst(sync_src, system)
            case dict():
                dest = sync_rule.get("dest")
                if not isinstance(dest, dict):
                    raise TypeError(
                        "The 'dest' field must be a dictionary mapping OS names to paths."
                    )
                dest_path = dest.get(system.lower())
                match dest_path:
                    case None:
                        yield _make_default_dst(sync_src, system)
                    case "":
                        yield None
                    case str():
                        yield Path.home() / dest_path
                    case _:
                        raise TypeError(
                            "The destination path must be a string, None, or empty string."
                        )


def _policies() -> Generator[Policy]:
    for sync_rule in LOADED_CONFIG.values():
        match sync_rule:
            case None:
                yield Policy.DEFAULT
            case dict():
                policy = sync_rule.get("policy")
                match policy:
                    case None:
                        yield Policy.DEFAULT
                    case str():
                        yield Policy[policy.upper()]
                    case _:
                        raise TypeError("The 'policy' field must be a string or leave it unset.")


def _parsed_sync_tasks(system: str) -> list[SyncTask]:
    return [
        make_sync_task(src_attr, dst, policy)
        for src_attr, dst, policy in zip(_src_attrs(), _dst_paths(system), _policies(), strict=True)
    ]


PARSED_SYNC_TASKS = {
    "Windows": _parsed_sync_tasks("Windows"),
    "Linux": _parsed_sync_tasks("Linux"),
}
