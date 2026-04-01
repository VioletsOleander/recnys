import platform
from enum import StrEnum

__all__ = ["Platform", "UnsupportedPlatformError", "get_platform"]


class UnsupportedPlatformError(RuntimeError):
    pass


class Platform(StrEnum):
    """Supported platforms of recnys.

    Attributes:
        WINDOWS
        LINUX
    """

    WINDOWS = "Windows"
    LINUX = "Linux"

    @classmethod
    def _missing_(cls, value: object) -> None:
        supported = ", ".join([repr(e.value) for e in cls])
        raise UnsupportedPlatformError(
            f"Unsupported platform: {value}. Currently only {supported} platforms are supported."
        )


def get_platform() -> Platform:
    """Detect the current platform and return it as a Platform enum member.

    Raises:
        UnsupportedPlatformError: If the current platform is not supported.
    """
    return Platform(platform.system())
