from pathlib import Path
from typing import TYPE_CHECKING

from recnys.backend.syncer import Syncer
from recnys.backend.task import CanonicalSyncTask
from recnys.frontend.task import Policy

from .constants import DST_CONTENT, SRC_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.backend.state import SyncState

__all__ = ["init_filesystem", "make_canonical_sync_tasks", "make_syncer"]


def make_canonical_sync_tasks(system: str) -> list[CanonicalSyncTask]:
    """Construct the expected CanonicalSyncTask objects.

    This function should be called after the fake filesystem is set up.
    """
    match system:
        case "Windows":
            return [
                CanonicalSyncTask(
                    src=Path.cwd() / ".vimrc",
                    dst=Path.home() / "_vimrc",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / ".gitconfig",
                    dst=Path.home() / ".gitconfig",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nvim/init.lua",
                    dst=Path.home() / "AppData/Local/nvim/init.lua",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nvim/lua/config/lazy.lua",
                    dst=Path.home() / "AppData/Local/nvim/lua/config/lazy.lua",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "yazi/yazi.toml",
                    dst=Path.home() / "AppData/Roaming/yazi/yazi.toml",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nushell/config.nu",
                    dst=Path.home() / "AppData/Roaming/nushell/config.nu",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nushell/env.nu",
                    dst=Path.home() / "AppData/Roaming/nushell/env.nu",
                    policy=Policy.OVERWRITE,
                ),
            ]
        case "Linux":
            return [
                CanonicalSyncTask(
                    src=Path.cwd() / ".vimrc",
                    dst=Path.home() / ".vimrc",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / ".bashrc",
                    dst=Path.home() / ".bashrc",
                    policy=Policy.SOURCE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / ".gitconfig",
                    dst=Path.home() / ".gitconfig",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nvim/init.lua",
                    dst=Path.home() / ".config/nvim/init.lua",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nvim/lua/config/lazy.lua",
                    dst=Path.home() / ".config/nvim/lua/config/lazy.lua",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "yazi/yazi.toml",
                    dst=Path.home() / ".config/yazi/yazi.toml",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nushell/config.nu",
                    dst=Path.home() / ".config/nushell/config.nu",
                    policy=Policy.OVERWRITE,
                ),
                CanonicalSyncTask(
                    src=Path.cwd() / "nushell/env.nu",
                    dst=Path.home() / ".config/nushell/env.nu",
                    policy=Policy.OVERWRITE,
                ),
            ]
        case _:
            raise NotImplementedError(f"Unsupported OS: {system}")


def make_syncer(state: SyncState, tasks: list[CanonicalSyncTask]) -> Syncer:
    """Construct a Syncer instance by injecting sync states and tasks."""
    syncer = object.__new__(Syncer)
    syncer.sync_state = state
    syncer.sync_tasks = tasks
    return syncer


def init_filesystem(
    filesystem: FakeFilesystem, canonical_sync_tasks: list[CanonicalSyncTask]
) -> FakeFilesystem:
    """Initialize the fake filesystem according to the given expected sync tasks.

    Create source files with sample content.
    If the policy is SOURCE, also create destination files with sample content.
    """
    for task in canonical_sync_tasks:
        src_file = task.src
        filesystem.create_file(file_path=src_file, contents=SRC_CONTENT)

        if task.policy == Policy.SOURCE:
            dst_file = task.dst
            filesystem.create_file(file_path=dst_file, contents=DST_CONTENT)

    return filesystem
