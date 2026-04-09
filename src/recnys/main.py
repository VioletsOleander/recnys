import argparse
import logging
from importlib.metadata import version

from .backend.grafter import TreeGrafter
from .backend.parser import ConfigParser
from .backend.refiner import TreeRefiner
from .backend.utils.serializer import deserialize_tree, serialize_tree
from .backend.utils.visualizer import print_tree
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
        "--silent",
        action="store_true",
        help="Suppress normal console output. This will not affect error messages.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Write debug information to log file. This will override the --silent option.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"v{version('recnys')}",
        help="Show version and exit",
    )
    return parser.parse_args()


@handle_exceptions
def main(argv: argparse.Namespace | None = None) -> int:
    args = parse_arguments() if argv is None else argv

    platform = get_platform()
    paths = make_paths(platform)
    setup_logging(paths.log_file, silent=args.silent, debug=args.debug)

    # Frontend
    # Load: yaml -> dict
    loaded_config = load_yaml(
        paths.recnys_file,
        note="Hint: Please run this command in the root of your dotfiles repository, "
        "where the recnys.yaml file is located.",
    )

    # Scan: dict -> liner model
    scanned_config = scan_config(loaded_config)

    # Backend
    # Parse: liner model -> tree model
    parser = ConfigParser(paths, platform)
    root = parser.parse(scanned_config)

    # Refine: expand 'copy' dir nodes
    refiner = TreeRefiner()
    root = refiner.refine(root)

    # Graft: add deleted nodes
    prev_root = deserialize_tree(paths.tree_file)
    if prev_root is not None:
        grafter = TreeGrafter()
        root = grafter.graft(root, prev_root)

    print_tree(root, verbose=True)

    return 0
