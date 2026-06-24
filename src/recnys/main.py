import argparse

from recnys import __version__

from .handler import handle_exceptions
from .logger import setup_logger
from .pipeline import BackendPipeline, FrontendPipeline


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="A helper for dotfiles synchronization",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Perform a dry run without making any changes.",
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
        version=__version__,
        help="Show version and exit",
    )
    return parser.parse_args()


@handle_exceptions
def main(argv: argparse.Namespace | None = None) -> int:
    args = parse_arguments() if argv is None else argv
    setup_logger(silent=args.silent, debug=args.debug)

    frontend = FrontendPipeline()
    scanned_config = frontend.run()

    backend = BackendPipeline()
    backend.run(scanned_config, dry_run=args.dry_run)

    return 0
