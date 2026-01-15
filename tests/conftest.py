from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from recnys.backend.task import CanonicalSyncTask
from recnys.testing.frontend.utils import make_sync_task

if TYPE_CHECKING:
    from collections.abc import Generator
    from unittest.mock import Mock

    from pytest_mock import MockerFixture

    from recnys.frontend.task import SyncTask


@pytest.fixture(params=["Linux", "Windows"])
def platform(mocker: MockerFixture, request: pytest.FixtureRequest) -> Mock:
    return mocker.patch("recnys.frontend.task.platform.system", return_value=request.param)


@pytest.fixture
def sync_tasks(platform: Mock) -> list[SyncTask]:
    from recnys.testing.frontend.constants import DST_PARAMS, POLICIES, SRC_PARAMS  # noqa: PLC0415

    return [
        make_sync_task(src_path=src_path, src_is_dir=src_is_dir, dst_path=dst_path, policy=policy)
        for (src_path, src_is_dir), dst_path, policy in zip(
            SRC_PARAMS, DST_PARAMS[platform.return_value], POLICIES, strict=True
        )
    ]


@pytest.fixture
def canonical_sync_tasks(platform: Mock) -> Generator[list[CanonicalSyncTask]]:
    from recnys.testing.backend.constants import DST_PATHS, POLICIES, SRC_PATHS  # noqa: PLC0415

    curr_os = platform.return_value
    for src_path in SRC_PATHS[curr_os]:
        src_path.parent.mkdir(parents=True, exist_ok=True)
        src_path.touch()

    yield [
        CanonicalSyncTask(src=src_path, dst=dst_path, policy=policy)
        for src_path, dst_path, policy in zip(
            SRC_PATHS[curr_os], DST_PATHS[curr_os], POLICIES[curr_os], strict=True
        )
    ]

    for src_path in SRC_PATHS[curr_os]:
        src_path.unlink()
