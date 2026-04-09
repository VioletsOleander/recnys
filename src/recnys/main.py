import argparse
import logging
from importlib.metadata import version

from .backend.creation.builder import CTreeBuilder
from .backend.creation.expander import CTreeExpander
from .backend.deletion.deriver import DTreeDeriver
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
    # Build: liner model -> creation tree
    builder = CTreeBuilder(paths, platform)
    ctree = builder.build(scanned_config)

    # Expand: expand 'copy' dir nodes
    expander = CTreeExpander()
    ctree = expander.expand(ctree)

    print_tree(ctree, verbose=True)

    # Derive: construct deletion tree
    prev_ctree = deserialize_tree(paths.ctree_file)
    if prev_ctree is not None:
        print_tree(prev_ctree, verbose=True)
        deriver = DTreeDeriver()
        dtree = deriver.derive(ctree, prev_ctree)

    # Merge: graft unfinished deletion nodes
    prev_dtree = deserialize_tree(paths.dtree_file)
    if prev_dtree is not None:
        print_tree(prev_dtree, verbose=True)

    print_tree(dtree, verbose=True)

    return 0
