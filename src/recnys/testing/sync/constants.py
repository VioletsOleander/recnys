from functools import cached_property
from pathlib import Path

__all__ = ["NORMAL_FILE_CONTENT", "LazyConstants"]

NORMAL_FILE_CONTENT = "Sample content for source files."


class _LazyConstants:
    @cached_property
    def record_file_path(self) -> Path:
        return Path.cwd() / ".recnys" / "sync_record.json"

    @cached_property
    def rendered_file_dir(self) -> Path:
        return Path.cwd() / ".recnys" / "rendered"


LazyConstants = _LazyConstants()
