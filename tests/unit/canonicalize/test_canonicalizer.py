from __future__ import annotations

from pyfakefs.fake_filesystem import FakeFilesystem
from recnys.testing.canonicalize.arrange import (
    create_source_files,
    make_canonical_config,
    make_canonicalizer,
)
from recnys.testing.load.constants import LOADED_CONFIG


def test_canonicalize(system: str, filesystem: FakeFilesystem) -> None:
    create_source_files(filesystem=filesystem)
    canonicalizer = make_canonicalizer()
    expected_canonical_config = make_canonical_config(system=system)

    result = canonicalizer.canonicalize(loaded_config=LOADED_CONFIG)

    assert result == expected_canonical_config
