"""Provide `TemplateRenderer` to render template files into actual files with content."""

import dataclasses
import logging
from pathlib import Path
from typing import TYPE_CHECKING, override

from jinja2 import Environment

from recnys.io.executor import FileIOTaskExecutor
from recnys.io.record import TaskExecutionDecision, TaskExecutionResult
from recnys.io.utils import get_normalized_file_hash

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
    _variables_file_path: Path | None

    def __init__(self, variables: LoadedVariables, variables_file_path: Path | None = None) -> None:
        """Initialize the template renderer with the given variables.

        Args:
            variables (LoadedVariables): The variables to be used for rendering templates.
            variables_file_path (Path | None): The path to the variables file for change detection.
        """
        self._variables = variables
        self._variables_file_path = variables_file_path
        self._environment = Environment(keep_trailing_newline=True, autoescape=False)  # noqa: S701

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
        # Check if variables file has changed
        variables_changed = False
        if self._variables_file_path and self._variables_file_path.exists():
            current_variables_hash = get_normalized_file_hash(self._variables_file_path)
            previous_variables_hash = last_record.metadata.get("variables_file_hash")
            
            if previous_variables_hash and previous_variables_hash != current_variables_hash:
                logger.info(
                    "Variables file has changed (hash: %s -> %s), forcing re-render of all templates",
                    previous_variables_hash[:8],
                    current_variables_hash[:8],
                )
                variables_changed = True
            
            # Mark all tasks to force execute if variables changed
            if variables_changed:
                tasks = [
                    dataclasses.replace(task, force_execute=True)
                    for task in tasks
                ]
        
        # Execute the tasks
        record = self.execute(tasks, last_record)
        
        # Store the current variables file hash in metadata
        if self._variables_file_path and self._variables_file_path.exists():
            record.metadata["variables_file_hash"] = get_normalized_file_hash(self._variables_file_path)
        
        return record

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
