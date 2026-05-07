__all__ = ["INVALID_CONFIGS"]

INVALID_CONFIGS = [
    {".foo": {"policy": "render"}},
    {".foo.template": {"policy": "symlink"}},
    {".foo.template": {"policy": "copy"}},
]
