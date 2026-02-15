import argparse
import logging
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
        "-f",
        "--force",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    project_data_dir = Path.cwd() / ".recnys"

    # Load config
    config_file = Path.cwd() / "recnys.yaml"
    config = load_config(file_path=config_file)

    # Canonicalize config
    canonicalizer = ConfigCanonicalizer(rendered_file_dir=project_data_dir / "rendered")
    canonical_config = canonicalizer.canonicalize(loaded_config=config)

    # Render
    logger.debug("Starting rendering...")

    render_tasks = build_render_tasks(config=canonical_config)

    variables_file = Path.cwd() / "variables.yaml"
    variables = load_variables(file_path=variables_file)

    render_record_file = project_data_dir / "render_record.json"
    render_record = ExecutionRecord.from_json(file_path=render_record_file)

    renderer = TemplateRenderer(variables=variables)
    render_record = renderer.render(tasks=render_tasks, last_record=render_record)
    render_record.save(file_path=render_record_file)

    logger.debug("Rendering complete.")
    logger.debug("Render record saved to %s", render_record_file)

    # Sync
    logger.info("Starting synchronization...")

    sync_tasks = build_sync_tasks(config=canonical_config)

    sync_record_file = project_data_dir / "sync_record.json"
    sync_record = ExecutionRecord.from_json(file_path=sync_record_file)

    syncer = FileSyncer(force=args.force)
    sync_record = syncer.sync(tasks=sync_tasks, last_record=sync_record)
    sync_record.save(file_path=sync_record_file)

    logger.info("Synchronization complete.")
    logger.info("Sync record saved to %s", sync_record_file)

    return 0
