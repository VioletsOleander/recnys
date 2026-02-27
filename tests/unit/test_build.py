import pytest

from recnys.build import build_render_tasks, build_sync_tasks
from recnys.testing.build.arrange import make_render_tasks, make_sync_tasks
from recnys.testing.canonicalize.arrange import make_canonical_config


@pytest.mark.usefixtures("filesystem")
def test_build_sync_tasks(system: str) -> None:
    expected_sync_tasks = make_sync_tasks(system=system)
    canonical_config = make_canonical_config(system=system)

    result = build_sync_tasks(config=canonical_config)

    assert result == expected_sync_tasks


@pytest.mark.usefixtures("filesystem")
def test_build_render_tasks(system: str) -> None:
    expected_render_tasks = make_render_tasks(system=system)
    canonical_config = make_canonical_config(system=system)

    result = build_render_tasks(config=canonical_config)

    assert result == expected_render_tasks
