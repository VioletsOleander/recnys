from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from recnys.frontend.task import Dst, Policy, Src, SyncTask

if TYPE_CHECKING:
    from collections.abc import Generator

    from recnys.frontend.load import LoadedConfig

__all__ = ["SrcAttr", "SyncTaskAttr", "make_parsed_sync_tasks", "make_sync_task"]


class SrcAttr(NamedTuple):
    path: Path
    is_dir: bool


class SyncTaskAttr(NamedTuple):
    src: SrcAttr
    dst: Path | None
    policy: Policy


def make_sync_task(sync_task_attr: SyncTaskAttr) -> SyncTask:
    """Create custom SyncTask by injecting given parameters."""
    src = object.__new__(Src)
    src.path = sync_task_attr.src.path
    src.is_dir = sync_task_attr.src.is_dir

    dst = object.__new__(Dst)
    dst.path = sync_task_attr.dst

    return SyncTask(src=src, dst=dst, policy=sync_task_attr.policy)


def _make_src_attrs(loaded_config: LoadedConfig) -> Generator[SrcAttr]:
    for sync_src in loaded_config:
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


def _make_dst_paths(loaded_config: LoadedConfig, system: str) -> Generator[Path | None]:
    if system not in ("Windows", "Linux"):
        raise NotImplementedError(f"Unsupported OS: {system}")

    for sync_src, sync_rule in loaded_config.items():
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


def _make_policies(loaded_config: LoadedConfig) -> Generator[Policy]:
    for sync_rule in loaded_config.values():
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


def make_parsed_sync_tasks(loaded_config: LoadedConfig, system: str) -> list[SyncTask]:
    """Create a list of parsed SyncTask based on given LoadedConfig and system name."""
    src_attrs = _make_src_attrs(loaded_config)
    dst_paths = _make_dst_paths(loaded_config, system)
    policies = _make_policies(loaded_config)

    return [
        make_sync_task(SyncTaskAttr(src=src_attr, dst=dst, policy=policy))
        for src_attr, dst, policy in zip(src_attrs, dst_paths, policies, strict=True)
    ]
