import logging
from typing import TYPE_CHECKING

from pydantic import ValidationError

from recnys.backend.model import RootNode

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

__all__ = ["deserialize_tree", "serialize_tree"]


def serialize_tree(root: RootNode, file_path: Path) -> None:
    """Dump the given root node to a json file."""
    logger.debug("Serializing data to %s", file_path)
    json_data = root.model_dump_json(indent=2)
    file_path.write_text(json_data, encoding="utf-8")
    logger.debug("Successfully serialized data to %s", file_path)


def deserialize_tree(file_path: Path) -> RootNode | None:
    """Load a root node from a json file, return None if unsuccessful."""
    try:
        logger.debug("Deserializing data from %s", file_path)
        data = file_path.read_text(encoding="utf-8")
        root = RootNode.model_validate_json(json_data=data)
    except FileNotFoundError:
        logger.debug("File %s not found, return None", file_path)
        return None
    except ValidationError:
        logger.debug("Data in file %s is invalid, return None", file_path)
        return None
    else:
        logger.debug("Successfully deserialized data from %s", file_path)
        return root
