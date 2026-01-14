import argparse
import logging
import sys
from pathlib import Path

from .backend.state import SyncState
from .backend.syncer import Syncer
from .frontend.load import load
from .frontend.parse import parse

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
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()

    config_file = Path.cwd() / "recnys.yaml"
    state_file = Path.cwd() / ".sync_state.json"

    try:
        sync_tasks = parse(load(config_file))
    except FileNotFoundError:
        logger.exception("Configuration file not found.")
        return 1
    except (TypeError, ValueError):
        logger.exception("Configuration file is malformed.")
        return 1
    except Exception:
        logger.exception("Failed to parse configuration file.")
        return 1

    sync_state = SyncState.from_json(state_file)
    syncer = Syncer(sync_state=sync_state, sync_tasks=sync_tasks)

    logger.info("Starting synchronization...")
    new_state = syncer.sync(force=args.force)
    logger.info("Synchronization complete.")

    logger.info("Saving synchronization state...")
    new_state.save(state_file)
    logger.info("State saved successfully.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
