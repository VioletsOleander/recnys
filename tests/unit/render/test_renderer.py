from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.testing.build.arrange import make_render_tasks
from recnys.testing.render.arrange import create_source_files, make_render_record, make_renderer
from recnys.testing.render.asserting import assert_render_record_io, assert_rendered_correctly


def test_render(system: str, filesystem: FakeFilesystem) -> None:
    render_tasks = make_render_tasks(system=system)
    create_source_files(filesystem=filesystem, tasks=render_tasks)
    record = make_render_record()
    renderer = make_renderer()

    record = renderer.render(tasks=render_tasks, last_record=record)

    assert_rendered_correctly(tasks=render_tasks)
    assert_render_record_io(render_record=record)
