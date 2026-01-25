from typing import TYPE_CHECKING

from recnys.backend.syncer import Syncer
from recnys.frontend.task import Policy

from .constants import DST_CONTENT, SRC_CONTENT

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem

    from recnys.backend.state import SyncState
    from recnys.backend.task import CanonicalSyncTask

__all__ = ["make_syncer", "prepare_filesystem", "sync_test"]


def make_syncer(state: SyncState, tasks: list[CanonicalSyncTask]) -> Syncer:
    """Make Syncer instance by injecting sync states and tasks."""
    syncer = object.__new__(Syncer)
    syncer.sync_state = state
    syncer.sync_tasks = tasks
    return syncer


def prepare_filesystem(
    filesystem: FakeFilesystem, canonicalized_sync_tasks: list[CanonicalSyncTask]
) -> FakeFilesystem:
    for task in canonicalized_sync_tasks:
        src_file = task.src
        filesystem.create_file(file_path=src_file, contents=SRC_CONTENT)

        if task.policy == Policy.SOURCE:
            dst_file = task.dst
            filesystem.create_file(file_path=dst_file, contents=DST_CONTENT)

    return filesystem


def sync_test(canonicalized_sync_tasks: list[CanonicalSyncTask]) -> None:
    """Test that files are synced correctly by the given sync tasks.

    It is assumed that the given tasks are correct. Therefore this function
    mainly used for backend testing where the tasks are directly given.

    The overall integration test should not rely on this function, because
    it does not test the task parsing and canonicalization logics.
    """
    for task in canonicalized_sync_tasks:
        assert task.dst.exists()
        with (
            task.src.open("r", encoding="utf-8") as src_file,
            task.dst.open("r", encoding="utf-8") as dst_file,
        ):
            if task.policy == Policy.OVERWRITE:
                assert src_file.read() == dst_file.read()
            elif task.policy == Policy.SOURCE:
                first_line = dst_file.readline().strip()
                assert first_line == f'source "{task.src}"'

                origin_content = dst_file.read().strip()
                assert origin_content == DST_CONTENT.strip()
