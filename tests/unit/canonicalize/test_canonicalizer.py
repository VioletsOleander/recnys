from typing import TYPE_CHECKING

from recnys.testing.canonicalize.arrange import (
    create_source_files,
    make_canonical_config,
    make_canonicalizer,
)
from recnys.testing.load.constants import LOADED_CONFIG

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


def test_canonicalize(system: str, filesystem: FakeFilesystem) -> None:
    create_source_files(filesystem=filesystem)
    canonicalizer = make_canonicalizer()
    expected_canonical_config = make_canonical_config(system=system)

    result = canonicalizer.canonicalize(loaded_config=LOADED_CONFIG)

    assert result == expected_canonical_config
