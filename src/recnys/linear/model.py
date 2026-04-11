"""Provide data models for scanned configuration and variables."""

from enum import StrEnum

from pydantic import BaseModel, RootModel, model_validator
from pydantic_core import InitErrorDetails, PydanticCustomError, ValidationError

__all__ = ["Dest", "EntryValue", "Policy", "ScannedConfig", "ScannedVariables"]


class Policy(StrEnum):
    """The file synchronization policy.

    Attributes:
        COPY: The source file will be copied to the destination path.
        RENDER: The source template file will be rendered to the destination path.
        SYMLINK: A symbolic link will be created at the destination path pointing to the source file.
    """

    COPY = "copy"
    RENDER = "render"
    SYMLINK = "symlink"


class Dest(BaseModel):
    """Destination paths for different platforms.

    Attributes:
        Linux (str | None): The destination path for Linux, or None if not specified.
        Windows (str | None): The destination path for Windows, or None if not specified.
    """

    Linux: str | None = None
    Windows: str | None = None


class EntryValue(BaseModel):
    """Scanned entry value.

    Attributes:
        dest (Dest | None): The destination paths for different platforms, or None if not specified.
        policy (Policy | None): The synchronization policy, or None if not specified.
    """

    dest: Dest | None = None
    policy: Policy | None = None


class ScannedConfig(RootModel):
    """Key-value pairs scanned from the YAML configuration data.

    Key (str): The source path.
    Value (EntryValue | None): The destination and policy, or None if not specified.
    """

    root: dict[str, EntryValue | None]

    @model_validator(mode="after")
    def check_policy(self) -> ScannedConfig:
        for key, val in self.root.items():
            if val is None or val.policy is None:
                continue

            is_template = key.endswith(".template")

            if is_template and val.policy == Policy.RENDER:
                continue
            if not is_template and val.policy != Policy.RENDER:
                continue

            message = (
                "Policy of template files must be 'render'"
                if is_template
                else "Only template files can have 'render' policy"
            )

            # Construct init error details in order to provide loc information
            detail = InitErrorDetails(
                type=PydanticCustomError("value_error", message),
                input=val.policy,
                loc=(key, "policy"),
            )
            raise ValidationError.from_exception_data(
                title=self.__class__.__name__, line_errors=[detail]
            )

        return self


class ScannedVariables(RootModel):
    """Key-value pairs scanned from the YAML variables data.

    Key (str): The name of the variable.
    Value (str): The value of the variable.
    """

    root: dict[str, str]
