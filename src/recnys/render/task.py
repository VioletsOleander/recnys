from dataclasses import dataclass, field

from recnys.io.task import FileIOTask

__all__ = ["TemplateRenderTask"]


@dataclass(frozen=True, kw_only=True)
class TemplateRenderTask(FileIOTask):
    """Representation of a template rendering task.

    See `FileIOTask` for more details.
    """

    name: str = field(default="Template Render Task", init=False)

    def __str__(self) -> str:
        return f"TemplateRenderTask(src={self.src}, dst={self.dst})"
