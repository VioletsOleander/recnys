from pathlib import Path

from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError

from .model import EntryValue, Policy, ScannedConfig

__all__ = ["validate_config"]


def _validate_val(key: str, val: EntryValue | None) -> None:
    if val is None or val.policy is None:
        return

    if key.endswith(".template"):
        if val.policy == Policy.RENDER:
            return
        message = "Policy of template files must be 'render'"
    else:
        if val.policy != Policy.RENDER:
            return
        message = "Only template files can have 'render' policy"

    # Construct init error details in order to provide loc information
    detail = InitErrorDetails(
        type=PydanticCustomError("value_error", message),
        input=val.policy,
        loc=(key, "policy"),
    )
    raise ValidationError.from_exception_data(title=ScannedConfig.__name__, line_errors=[detail])


def _validate_key(key: str) -> None:
    src = Path.cwd() / key

    if key.endswith("/"):
        if src.is_dir():
            return
        message = "Specified source directory does not exists"
    else:
        if src.is_file():
            return
        message = "Specified source file does not exists"

    message += "\nHint: Please check recnys.yaml to ensure the specified path exists"

    # Construct init error details in order to provide loc information
    detail = InitErrorDetails(
        type=PydanticCustomError("key_error", message),
        input=key,
        loc=(key,),
    )
    raise ValidationError.from_exception_data(title=ScannedConfig.__name__, line_errors=[detail])


def validate_config(scanned_config: ScannedConfig) -> None:
    """Validate the scanned configuration.

    This validation process focuses on the semantic of the scanned configuration,
    as compared to the type safety validation provided by Pydantic.

    Args:
        scanned_config (ScannedConfig): The scanned configuration to validate.

    Raises:
        ValidationError: If any validation error occurs.
    """
    for key, val in scanned_config.root.items():
        _validate_key(key)
        _validate_val(key, val)
