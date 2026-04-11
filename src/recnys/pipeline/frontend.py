from pathlib import Path
from typing import TYPE_CHECKING

from recnys.linear.scanner import scan_config
from recnys.utils.loader import load_yaml

if TYPE_CHECKING:
    from recnys.linear.model import ScannedConfig

__all__ = ["FrontendPipeline"]


class FrontendPipeline:
    """FrontendPipeline orchestrates the frontend pipeline.

    The frontend pipeline includes loading and scanning the configuration.

    The main provided method is `run`.
    """

    _recnys_file: Path

    def __init__(self) -> None:
        """Initialize the FrontendPipeline, preparing necessary resources for the pipeline execution."""
        self._arrange()

    def run(self) -> ScannedConfig:
        """Run the frontend pipeline, returning the scanned configuration.

        Returns:
            ScannedConfig: The scanned configuration.
        """
        # Load: yaml -> dict
        loaded_config = load_yaml(
            self._recnys_file,
            note="Hint: Please run this command in the root of your dotfiles repository, "
            "where the recnys.yaml file is located.",
        )

        # Scan: dict -> linear model
        return scan_config(loaded_config)

    def _arrange(self) -> None:
        self._recnys_file = Path.cwd() / "recnys.yaml"
