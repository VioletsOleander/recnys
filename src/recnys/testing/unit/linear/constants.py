from recnys.linear.model import ScannedConfig

__all__ = ["INVALID_CONFIGS", "SOURCE_FILES"]

SOURCE_FILES = (
    ".foo",
    ".foo.template",
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
