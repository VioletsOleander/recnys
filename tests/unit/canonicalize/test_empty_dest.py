"""Test that empty string destination specification is respected."""

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from recnys.canonicalize.canonicalizer import ConfigCanonicalizer

if TYPE_CHECKING:
    from pyfakefs.fake_filesystem import FakeFilesystem


@pytest.fixture
def setup_test_files(filesystem: FakeFilesystem) -> None:
    """Create test files for the empty dest test."""
    # Create directory structure
    filesystem.create_file(Path.cwd() / "nushell/third_party/file1.txt")
    filesystem.create_file(Path.cwd() / "nushell/third_party/subdir/file2.txt")
    filesystem.create_file(
        Path.cwd() / "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu"
    )


def test_empty_dest_excludes_directory_files(
    system: str,
    filesystem: FakeFilesystem,
    setup_test_files: None,  # noqa: ARG001
) -> None:
    """Test that files under a directory with empty dest are not synced."""
    # Setup
    loaded_config = {
        "nushell/third_party/": {"dest": {system: ""}},
    }

    canonicalizer = ConfigCanonicalizer(rendered_file_dir=Path.cwd() / ".recnys/rendered")

    # Act
    result = canonicalizer.canonicalize(loaded_config=loaded_config)

    # Assert - all expanded files should have dst=None
    for key, value in result.items():
        assert value.sync_spec.dst is None, (
            f"File {key} should have dst=None but got {value.sync_spec.dst}"
        )


def test_empty_dest_excludes_explicit_files_under_directory(
    system: str,
    filesystem: FakeFilesystem,
    setup_test_files: None,  # noqa: ARG001
) -> None:
    """Test that explicitly listed files under excluded directory are also excluded."""
    # Setup - this is the bug case from the issue
    loaded_config = {
        "nushell/third_party/": {"dest": {system: ""}},
        "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu": None,
    }

    canonicalizer = ConfigCanonicalizer(rendered_file_dir=Path.cwd() / ".recnys/rendered")

    # Act
    result = canonicalizer.canonicalize(loaded_config=loaded_config)

    # Assert - the explicit file should NOT be in the result because it's under an excluded dir
    explicit_file_key = "nushell/third_party/nu_scripts/custom-completions/git/git-completions.nu"
    assert explicit_file_key not in result, (
        f"Explicitly listed file {explicit_file_key} should not be synced "
        "because it's under an excluded directory"
    )

    # All files in result should have dst=None (from directory expansion)
    for key, value in result.items():
        assert value.sync_spec.dst is None, (
            f"File {key} should have dst=None but got {value.sync_spec.dst}"
        )


def test_empty_dest_allows_explicit_files_outside_excluded_directory(
    system: str,
    filesystem: FakeFilesystem,
    setup_test_files: None,  # noqa: ARG001
) -> None:
    """Test that explicitly listed files outside excluded directory are still synced."""
    # Setup
    filesystem.create_file(Path.cwd() / "nushell/other_file.txt")

    loaded_config = {
        "nushell/third_party/": {"dest": {system: ""}},
        "nushell/other_file.txt": None,
    }

    canonicalizer = ConfigCanonicalizer(rendered_file_dir=Path.cwd() / ".recnys/rendered")

    # Act
    result = canonicalizer.canonicalize(loaded_config=loaded_config)

    # Assert - other_file.txt should be in result with a destination
    assert "nushell/other_file.txt" in result
    assert result["nushell/other_file.txt"].sync_spec.dst is not None

    # Files under third_party should have dst=None
    for key, value in result.items():
        if "third_party" in key:
            assert value.sync_spec.dst is None


def test_explicit_file_with_custom_dest_under_excluded_dir(
    system: str,
    filesystem: FakeFilesystem,
    setup_test_files: None,  # noqa: ARG001
) -> None:
    """Test that explicit file with custom dest under excluded dir CAN override.

    When a file has an explicit dest specification, it should override the
    parent directory exclusion. This allows users to sync specific files
    from an excluded directory.
    """
    # Setup - explicit dest should override parent exclusion
    loaded_config = {
        "nushell/third_party/": {"dest": {system: ""}},
        "nushell/third_party/file1.txt": {"dest": {system: "custom/path"}},
    }

    canonicalizer = ConfigCanonicalizer(rendered_file_dir=Path.cwd() / ".recnys/rendered")

    # Act
    result = canonicalizer.canonicalize(loaded_config=loaded_config)

    # Assert - the explicit file SHOULD be in result with custom dest
    assert "nushell/third_party/file1.txt" in result, (
        "Explicitly listed file with custom dest should override parent directory exclusion"
    )
    expected_dest = Path.home() / "custom/path"
    assert result["nushell/third_party/file1.txt"].sync_spec.dst == expected_dest


def test_explicit_file_with_empty_dest_under_excluded_dir(
    system: str,
    filesystem: FakeFilesystem,
    setup_test_files: None,  # noqa: ARG001
) -> None:
    """Test that explicit file with empty dest under excluded dir is handled.

    When a file has an explicit empty dest, it should be in the canonical config
    with dst=None, but will be filtered out during task building.
    """
    # Setup - explicit empty dest overrides parent exclusion but also excludes the file
    loaded_config = {
        "nushell/third_party/": {"dest": {system: ""}},
        "nushell/third_party/file1.txt": {"dest": {system: ""}},
    }

    canonicalizer = ConfigCanonicalizer(rendered_file_dir=Path.cwd() / ".recnys/rendered")

    # Act
    result = canonicalizer.canonicalize(loaded_config=loaded_config)

    # Assert - the explicit file should be in result but with dst=None
    assert "nushell/third_party/file1.txt" in result, (
        "Explicitly listed file with empty dest should be in canonical config"
    )
    assert result["nushell/third_party/file1.txt"].sync_spec.dst is None
