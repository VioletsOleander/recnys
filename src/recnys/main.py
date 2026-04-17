import argparse

from .arranger import arrange
from .handler import handle_exceptions
from .pipeline import BackendPipeline, FrontendPipeline


def version() -> str:
    import importlib.metadata  # noqa: PLC0415

    return f"v{importlib.metadata.version('recnys')}"


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
        version=version(),
        help="Show version and exit",
    )
    return parser.parse_args()


@handle_exceptions
def main(argv: argparse.Namespace | None = None) -> int:
    args = parse_arguments() if argv is None else argv

    arrange(args)

    pipeline = FrontendPipeline()
    scanned_config = pipeline.run()

    pipeline = BackendPipeline()
    pipeline.run(scanned_config, dry_run=args.dry_run)

    return 0
