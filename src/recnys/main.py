import argparse
import logging
import shutil
from pathlib import Path

from .build import build_render_tasks, build_sync_tasks
from .canonicalize.canonicalizer import ConfigCanonicalizer
from .io.record import ExecutionRecord
from .load import load_config, load_variables
from .render.renderer import TemplateRenderer
from .sync.syncer import FileSyncer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Dotfiles synchronization helper",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-s",
        "--skip-confirmation",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "-r",
        "--force-render",
        action="store_true",
        help="Force execute all render tasks, ignoring execution decisions",
    )
    parser.add_argument(
        "-c",
        "--force-sync",
        action="store_true",
        help="Force execute all sync tasks, ignoring execution decisions",
    )
    parser.add_argument(
        "-o",
        "--render-only",
        action="store_true",
        help="Only perform rendering without synchronization",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean all cached data and execution records in project data directory",
    )
    return parser.parse_args()


# TODO: based on configuration entry change to make execution decision
# in addition to current implementation
# This may again incur significant refactoring, because current implementation
# separates the decision making from the configuration parsing. The decision
# making is purely based on the task and the execution record.
# Current workaround is to add a `force_execute` attribute to the task.
def main() -> int:
    args = parse_arguments()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    project_data_dir = Path.cwd() / ".recnys"
    if args.clean:
        shutil.rmtree(project_data_dir)
        logger.info("Cleaned all cached data and execution records in %s", project_data_dir)
        return 0

    # Load config
    config_file = Path.cwd() / "recnys.yaml"
    config = load_config(file_path=config_file)

    # Canonicalize config
    canonicalizer = ConfigCanonicalizer(rendered_file_dir=project_data_dir / "rendered")
    canonical_config = canonicalizer.canonicalize(loaded_config=config)

    # Render
    logger.info("Starting rendering...")
    render_tasks = build_render_tasks(config=canonical_config, force_execute=args.force_render)

    if render_tasks:
        variables_file = Path.cwd() / "variables.yaml"
        variables = load_variables(file_path=variables_file)

        render_record_file = project_data_dir / "render_record.json"
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

    sync_record_file = project_data_dir / "sync_record.json"
    sync_record = ExecutionRecord.from_json(file_path=sync_record_file)

    syncer = FileSyncer(skip=args.skip_confirmation)
    sync_record = syncer.sync(tasks=sync_tasks, last_record=sync_record)
    sync_record.save(file_path=sync_record_file)

    logger.info("Synchronization complete.")
    logger.info("Sync record saved to %s", sync_record_file)

    return 0
