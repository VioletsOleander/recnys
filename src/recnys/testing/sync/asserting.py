from recnys.sync.task import FileSyncPolicy, FileSyncTask
from recnys.testing.render.constants import RENDERED_CONTENT

from .constants import NORMAL_FILE_CONTENT, LazyConstants


def assert_synced_correctly(tasks: list[FileSyncTask]) -> None:
    for task in tasks:
        file_path = task.dst
        assert file_path.exists(), f"Expected file {file_path} to exist, but it does not."

        expected_content = (
            RENDERED_CONTENT
            if task.src.is_relative_to(LazyConstants.rendered_file_dir)
            else NORMAL_FILE_CONTENT
        )
        expected_content = (
            f'source "{task.src}"' if task.policy == FileSyncPolicy.SOURCE else expected_content
        )
        expected_content = expected_content.strip()
        content = file_path.read_text().strip()
        assert content == expected_content, (
            f"Expected content of {file_path} to be '{expected_content}', but got '{content}'."
        )
