from typing import TYPE_CHECKING

from recnys.io.record import ExecutionRecord

from .constants import RENDERED_CONTENT, LazyConstants

if TYPE_CHECKING:
    from recnys.render.task import TemplateRenderTask

__all__ = ["assert_rendered_correctly"]


def assert_rendered_correctly(tasks: list[TemplateRenderTask]) -> None:
    for task in tasks:
        file_path = task.dst
        assert file_path.exists(), f"Expected file {file_path} to exist, but it does not."

        content = file_path.read_text()
        assert content == RENDERED_CONTENT, (
            f"Expected content of {file_path} to be '{RENDERED_CONTENT}', but got '{content}'."
        )


def assert_render_record_io(render_record: ExecutionRecord) -> None:
    render_record.save(file_path=LazyConstants.record_file_path)
    loaded_render_record = ExecutionRecord.from_json(file_path=LazyConstants.record_file_path)
    assert loaded_render_record == render_record, (
        "Loaded render record does not match the original."
    )
