from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.io.record import ExecutionRecord
from recnys.render.renderer import TemplateRenderer
from recnys.render.task import TemplateRenderTask
from recnys.testing.load.constants import LOADED_VARIABLES

from .constants import TEMPLATE_FILE_CONTENT, LazyConstants

__all__ = ["create_source_files", "make_render_record", "make_renderer"]


def create_source_files(filesystem: FakeFilesystem, tasks: list[TemplateRenderTask]) -> None:
    for task in tasks:
        file_path = task.src
        filesystem.create_file(file_path=file_path, contents=TEMPLATE_FILE_CONTENT)


def make_render_record() -> ExecutionRecord:
    """Construct and return an empty ExecutionRecord for rendering.

    This function should be called after the fake filesystem is set up.
    """
    return ExecutionRecord.from_json(file_path=LazyConstants.record_file_path)


def make_renderer() -> TemplateRenderer:
    """Construct and return a TemplateRenderer.

    This function should be called after the fake filesystem is set up.
    """
    return TemplateRenderer(variables=LOADED_VARIABLES)
