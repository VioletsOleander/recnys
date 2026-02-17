import hashlib
from pathlib import Path

__all__ = ["get_normalized_file_hash"]


def get_normalized_file_hash(file_path: Path) -> str:
    """Compute file hash, ignoring differences in line endings."""
    sha256 = hashlib.sha256()

    # utilize universal newline mode to normalize line endings
    with file_path.open("r", encoding="utf-8") as f:
        while chunk := f.read(8192):
            sha256.update(chunk.encode("utf-8"))

    return sha256.hexdigest()
