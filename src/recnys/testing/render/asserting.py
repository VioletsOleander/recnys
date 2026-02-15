from typing import TYPE_CHECKING

from .constants import RENDERED_CONTENT

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
