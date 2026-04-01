import argparse
import logging
from importlib.metadata import version
from pathlib import Path

from .build import build_render_tasks, build_sync_tasks
from .canonicalize.canonicalizer import ConfigCanonicalizer
from .config.loader import load_config, load_variables
from .io.record import ExecutionRecord
from .render.renderer import TemplateRenderer
from .sync.syncer import FileSyncer
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

    paths = make_paths()
    platform = get_platform()
    setup_logging(log_file=paths.log_file, debug=args.debug)

    # Load config
    config = load_config(file_path=paths.config_file)

    # Canonicalize config
    canonicalizer = ConfigCanonicalizer(platform=platform)
    canonical_config = canonicalizer.canonicalize(loaded_config=config)

    # Render
    render_tasks = build_render_tasks(force_execute=args.force_render, config=canonical_config)

    if render_tasks:
        logger.info("Starting rendering...")
        variables_file = Path.cwd() / "variables.yaml"
        variables = load_variables(file_path=variables_file)

        render_record_file = data_dir / "render_record.json"
        render_record = ExecutionRecord.from_json(file_path=render_record_file)

        renderer = TemplateRenderer(variables=variables)
        render_record = renderer.render(tasks=render_tasks, last_record=render_record)
        render_record.save(file_path=render_record_file)

        logger.info("Rendering complete.")
        logger.info("Render record saved to %s", render_record_file)

    if args.render_only:
        logger.info("Render-only mode enabled, skipping synchronization.")
        return 0

    # Sync
    logger.info("Starting synchronization...")
    sync_tasks = build_sync_tasks(config=canonical_config, force_execute=args.force_sync)

    sync_record_file = data_dir / "sync_record.json"
    sync_record = ExecutionRecord.from_json(file_path=sync_record_file)

    syncer = FileSyncer(skip=args.skip_confirmation)
    sync_record = syncer.sync(tasks=sync_tasks, last_record=sync_record)
    sync_record.save(file_path=sync_record_file)

    logger.info("Synchronization complete.")
    logger.info("Sync record saved to %s", sync_record_file)

    return 0
