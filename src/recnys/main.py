import argparse
import logging
from importlib.metadata import version
from pathlib import Path

from .backend.grafter import TreeGrafter
from .backend.parser import ConfigParser
from .backend.refiner import TreeRefiner
from .frontend.loader import load_yaml
from .frontend.scanner import scan_config
from .utils.exception import handle_exceptions
from .utils.logging import setup_logging
from .utils.paths import make_paths
from .utils.platform import get_platform

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A helper for dotfiles synchronization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--skip-confirmation",
        action="store_true",
        help="Skip confirmation prompts during synchronization",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"v{version('recnys')}",
        help="Show version and exit",
    )
    return parser.parse_args()


@handle_exceptions
def main() -> int:
    args = parse_arguments()

    platform = get_platform()
    paths = make_paths(platform)
    setup_logging(paths.log_file, debug=args.debug)

    # Frontend
    # Load
    loaded_config = load_yaml(
        paths.recnys_file,
        note="Hint: Please run this command in the root of your dotfiles repository, "
        "where the recnys.yaml file is located.",
    )

    # Scan
    scanned_config = scan_config(loaded_config)

    # Backend
    # Parse
    parser = ConfigParser(paths, platform)
    root = parser.parse(scanned_config)

    x = root.model_dump_json(indent=2)
    import pydantic
    from .backend.model import RootNode
    y = RootNode.model_validate_json(x)
    print(x)
    print(y)

    raise KeyboardInterrupt

    # Refine
    refiner = TreeRefiner()
    root = refiner.refine(root)

    # Graft
    grafter = TreeGrafter()
    # grafter.graft(root)

    return 0
