from functools import cached_property
from pathlib import Path

__all__ = ["RENDERED_CONTENT", "TEMPLATE_FILE_CONTENT", "LazyConstants"]

TEMPLATE_FILE_CONTENT = "Proxy URL: {{ proxy_url }}"
RENDERED_CONTENT = "Proxy URL: http://proxy.example.com:8080"


class _LazyConstants:
    @cached_property
    def record_file_path(self) -> Path:
        return Path.cwd() / ".recnys" / "render_record.json"


LazyConstants = _LazyConstants()
