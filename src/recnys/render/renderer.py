"""Provide `TemplateRenderer` to render template files into actual files with content."""

import logging
from typing import TYPE_CHECKING, override

from jinja2 import Environment

from recnys.io.executor import FileIOTaskExecutor
from recnys.io.record import TaskExecutionDecision, TaskExecutionResult

from .task import TemplateRenderTask

logger = logging.getLogger(__name__)

__all__ = ["TemplateRenderer"]

if TYPE_CHECKING:
    from recnys.io.record import ExecutionRecord
    from recnys.load import LoadedVariables


class TemplateRenderer(FileIOTaskExecutor[TemplateRenderTask]):
    """TemplateRenderer is responsible for rendering template files into actual files with content.

    It implements FileIOTaskExecutor, which allows it to make execution decisions and execute
    file I/O tasks sequentially, while maintaining an execution record.

    The main provided method is `render`.
    """

    _environment: Environment
    _variables: LoadedVariables

    def __init__(self, variables: LoadedVariables) -> None:
        """Initialize the template renderer with the given variables.

        Args:
            variables (LoadedVariables): The variables to be used for rendering templates.
        """
        self._variables = variables
        self._environment = Environment(keep_trailing_newline=True, autoescape=True)

    def render(
        self, tasks: list[TemplateRenderTask], last_record: ExecutionRecord
    ) -> ExecutionRecord:
        """Execute the template rendering tasks sequentially, while maintaining an execution record.

        Args:
            tasks (list[TemplateRenderTask]): The list of template rendering tasks to be executed.
            last_record (ExecutionRecord): The execution record of the last execution.

        Returns:
            ExecutionRecord: The execution record of the current execution,
                which will be used for future reference
        """
        return self.execute(tasks, last_record)

    @override
    def _execute_task(
        self, task: TemplateRenderTask, decision: TaskExecutionDecision
    ) -> TaskExecutionResult:
        """Execute the template rendering task based on the execution decision.

        Render the template file into actual file with content.

        Args:
            task (TemplateRenderTask): The template rendering task to be executed.
            decision (TaskExecutionDecision): The decision on whether and why to execute the task.

        Returns:
            TaskExecutionResult: The result of the task execution.
        """
        if decision.ok is False:
            logger.debug(
                "Skipping rendering for %s based on decision: %s", task.src, decision.reason
            )
            return TaskExecutionResult.SKIPPED

        try:
            logger.debug("Rendering template %s to %s...", task.src, task.dst)
            template_content = task.src.read_text(encoding="utf-8")
            template = self._environment.from_string(template_content)
            content = template.render(self._variables)

            task.dst.parent.mkdir(parents=True, exist_ok=True)

            tmp_dst = task.dst.with_suffix(task.dst.suffix + ".tmp")
            tmp_dst.write_text(content, encoding="utf-8")
            tmp_dst.replace(task.dst)

            logger.debug("Successfully rendered template %s to %s", task.src, task.dst)
        except Exception:
            logger.exception("Failed to render template %s to %s", task.src, task.dst)
            return TaskExecutionResult.FAILURE
        else:
            return TaskExecutionResult.SUCCESS
        finally:
            tmp_dst.unlink(missing_ok=True)
            logger.debug("Cleaned up temporary file %s", tmp_dst)
