from argparse import Namespace
from typing import TYPE_CHECKING

from recnys.main import main
from recnys.testing.arranger import create_config_files, create_source_files, setup_cwd
from recnys.testing.integration.constants import SOURCE_FILES

if TYPE_CHECKING:
    from pathlib import Path

    from pyfakefs.fake_filesystem import FakeFilesystem


def test_integration(resources_dir: Path, filesystem: FakeFilesystem) -> None:
    setup_cwd(filesystem)
    create_config_files(filesystem, resources_dir=resources_dir)
    create_source_files(filesystem, source_files=SOURCE_FILES)
    args = Namespace(silent=True, debug=False, dry_run=False)

    # Un-decorate the main function
    main.__wrapped__(args)  # type: ignore[ty:unresolved-attribute]
