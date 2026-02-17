from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem

__all__ = ["create_config_file", "create_variables_file"]


def create_config_file(filesystem: FakeFilesystem) -> Path:
    """Create the config file in the fake filesystem.

    Return the path to the created config file.
    """
    path = LazyConstants.config_file_path
    filesystem.create_file(file_path=path, contents=CONFIG_FILE_CONTENT)

    return path


def create_variables_file(filesystem: FakeFilesystem) -> Path:
    """Create the variables file in the fake filesystem.

    Return the path to the created variables file.
    """
    path = LazyConstants.variables_file_path
    filesystem.create_file(file_path=path, contents=VARIABLES_FILE_CONTENT)

    return path
