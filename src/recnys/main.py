import argparse
import logging
from importlib.metadata import version

from .backend.ctree.builder import CTreeBuilder
from .backend.ctree.expander import CTreeExpander
from .backend.dtree.builder import DTreeBuilder
# from .backend.utils.serializer import deserialize_tree, serialize_tree
from .backend.utils.visualizer import print_tree
from .frontend.loader import load_yaml
from .frontend.scanner import scan_config
from .utils.exception import handle_exceptions
from .utils.logging import setup_logging
from .utils.paths import get_paths
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
    paths = get_paths(platform)
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
    # Build ctree
    builder = CTreeBuilder(paths, platform)
    ctree = builder.build(scanned_config)

    # Expand ctree
    expander = CTreeExpander()
    ctree = expander.expand(ctree)

    print("Creation tree to execute:")
    print_tree(ctree, verbose=True)

    raise NotImplementedError("DTree building and execution is not implemented yet.")


    # Build dtree
    ctree_fexist = paths.ctree_file.exists()
    dtree_fexist = paths.dtree_file.exists()

    if ctree_fexist != dtree_fexist:
        e = RuntimeError(
            "Ctree file and dtree file are not consistent. "
            f"Please ensure that both {paths.ctree_file} and {paths.dtree_file} exist, "
            "or both of them do not exist."
        )
        e.add_note(
            "Hint: If backup files are available, please use them to recover the missing file. "
            "Otherwise, delete the existing file."
        )
        raise e

    if ctree_fexist:
        prev_ctree = deserialize_tree(paths.ctree_file)
        prev_dtree = deserialize_tree(paths.dtree_file)
        builder = DTreeBuilder()
        dtree = builder.build(ctree, prev_ctree, prev_dtree)
    else:
        pass

    print_tree(dtree, verbose=True)

    return 0
