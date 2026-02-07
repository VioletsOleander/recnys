from typing import TYPE_CHECKING

from recnys.frontend.task import Policy

from .constants import DST_CONTENT

if TYPE_CHECKING:
    from recnys.backend.task import CanonicalSyncTask


__all__ = ["sync_test"]


def sync_test(canonical_sync_tasks: list[CanonicalSyncTask]) -> None:
    """Test that files are synced correctly by the given sync tasks.

    It is assumed that the given tasks are correct. Therefore this function
    mainly used for backend testing where the tasks are directly given.

    The overall integration test should not rely on this function, because
    it does not test the task parsing and canonicalization logics.
    """
    for task in canonical_sync_tasks:
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
