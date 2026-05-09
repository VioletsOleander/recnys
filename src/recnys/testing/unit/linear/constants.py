from recnys.linear.model import ScannedConfig

__all__ = ["SCANNED_CONFIGS", "SOURCE_FILES"]

SOURCE_FILES = (
    ".foo",
    ".foo.template",
)

_LOADED_CONFIGS = (
    # Invalid policy
    {".foo": {"policy": "render"}},
    {".foo.template": {"policy": "symlink"}},
    {".foo.template": {"policy": "copy"}},
    # Non-existent source
    {".foo.bar": None},
    {".foo.bar.template": None},
    {"foo/bar": None},
)

SCANNED_CONFIGS = map(ScannedConfig.model_validate, _LOADED_CONFIGS)
