"""Shared constants for unit and integration tests."""

from pathlib import Path

__all__ = ["CTREE_FNAME", "DTREE_FNAME", "RECNYS_FNAME", "VARIABLES_FNAME", "LazyConstants"]

RECNYS_FNAME = "recnys.yaml"
VARIABLES_FNAME = "variables.yaml"
CTREE_FNAME = "prev_ctree.json"
DTREE_FNAME = "prev_dtree.json"


class _LazyConstants:
    @property
    def cwd(self) -> Path:
        """Current working directory."""
        return Path.home() / "repo"

    @property
    def data_dir(self) -> Path:
        """Data directory path."""
        return self.cwd / ".recnys"

    @property
    def recnys_file(self) -> Path:
        """Path to the recnys.yaml file."""
        return self.cwd / RECNYS_FNAME

    @property
    def variables_file(self) -> Path:
        """Path to the variables.yaml file."""
        return self.cwd / VARIABLES_FNAME

    @property
    def ctree_file(self) -> Path:
        """Path to the prev_ctree.json file."""
        return self.data_dir / CTREE_FNAME

    @property
    def dtree_file(self) -> Path:
        """Path to the prev_dtree.json file."""
        return self.data_dir / DTREE_FNAME


LazyConstants = _LazyConstants()
