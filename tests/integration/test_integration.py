from argparse import Namespace

from pyfakefs.fake_filesystem import FakeFilesystem

from recnys.main import main
from recnys.testing.integration.arrange import (
    change_cwd,
    create_recnys_file,
    create_source_files,
    create_variables_file,
)


def test_integration(system: str, filesystem: FakeFilesystem) -> None:
    print("\nSystem:", system)
    change_cwd(filesystem)
    create_recnys_file(filesystem)
    create_variables_file(filesystem)
    create_source_files(filesystem)
    args = Namespace(silent=False, debug=False)

    # Un-decorate the main function
    main.__wrapped__(args)  # type: ignore[unresolved-attribute]
