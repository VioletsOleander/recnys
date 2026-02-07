from typing import TYPE_CHECKING

from recnys.backend.task import canonicalize_sync_tasks
from recnys.testing.backend.arranger import init_filesystem, make_canonical_sync_tasks
from recnys.testing.frontend.arranger import make_sync_tasks

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_canonicalization(filesystem: FakeFilesystem, system: str) -> None:
    expected_tasks = make_canonical_sync_tasks(system)
    init_filesystem(filesystem=filesystem, canonical_sync_tasks=expected_tasks)

    parsed_sync_tasks = make_sync_tasks(system)
    result_tasks = canonicalize_sync_tasks(parsed_sync_tasks)

    for result, expected in zip(
        sorted(result_tasks, key=lambda x: x.src),
        sorted(expected_tasks, key=lambda x: x.src),
        strict=True,
    ):
        assert result == expected
