from argparse import Namespace
from pathlib import Path

from pyfakefs.fake_filesystem import FakeFilesystem

from recnys.main import main
from recnys.testing.integration.arrange import (
    change_cwd,
    create_config_files,
    create_data_files,
    create_source_files,
)


def test_integration(resources_dir: Path, system: str, filesystem: FakeFilesystem) -> None:
    change_cwd(filesystem)
    create_config_files(filesystem, resources_dir)
    create_data_files(filesystem, resources_dir, system)
    create_source_files(filesystem)
    args = Namespace(silent=False, debug=False)

    # Un-decorate the main function
    main.__wrapped__(args)  # type: ignore[unresolved-attribute]
