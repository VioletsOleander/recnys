from recnys.linear.model import ScannedConfig
from recnys.testing.constants import NORMAL_CONTENT, TEMPLATE_CONTENT
from recnys.testing.node import File

__all__ = ["INVALID_CONFIGS", "SOURCES"]

SOURCES = (
    File(path=".foo", content=NORMAL_CONTENT),
    File(path=".foo.template", content=TEMPLATE_CONTENT),
)

_INVALID_LOADED_CONFIGS = (
    # Invalid policy
    {".foo": {"policy": "render"}},
    {".foo.template": {"policy": "symlink"}},
    {".foo.template": {"policy": "copy"}},
    # Non-existent source
    {".foo.bar": None},
    {".foo.bar.template": None},
    {"foo/bar": None},
)

_INVALID_SCANNED_CONFIGS = map(ScannedConfig.model_validate, _INVALID_LOADED_CONFIGS)

INVALID_CONFIGS = _INVALID_SCANNED_CONFIGS
