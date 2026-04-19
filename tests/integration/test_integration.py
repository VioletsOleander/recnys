from argparse import Namespace
from typing import TYPE_CHECKING

from recnys.main import main
from recnys.testing.integration.arranger import change_cwd, create_config_files, create_source_files

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem


def test_integration(resources_dir: Path, filesystem: FakeFilesystem) -> None:
    change_cwd(filesystem)
    create_config_files(filesystem, resources_dir)
    create_source_files(filesystem)
    args = Namespace(silent=False, debug=True, dry_run=False)

    # Un-decorate the main function
    main.__wrapped__(args)  # type: ignore[unresolved-attribute]
