import argparse
import hashlib
import json
import sys
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Any


class Policy(StrEnum):
    APPEND = "append"
    OVERWRITE = "overwrite"
    PREPEND_SOURCE_STATEMENT = "prepend_source_statement"


EXCLUDE_PATTERNS = [
    ".git/",
    "__pycache__/",
    "debug_home/",
    ".gitignore",
    ".sync_state.json",
    "setup.py",
    "setup.sh",
    "README.md",
]


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Synchronize configuration files to home directory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--append",
        action="store_true",
        help="Set default sync policy to append",
    )
    group.add_argument(
        "--overwrite",
        action="store_true",
        default=True,
        help="Set default sync policy to overwrite (default behavior)",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "--show_state",
        action="store_true",
        help="Do not sync, just show current sync states",
    )
    parser.add_argument(
        "--clear_state",
        action="store_true",
        help="Do not sync, just clear all sync states",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode, which switch target directory to ./debug_home",
    )

    args = parser.parse_args()

    return args


class ConfigSyncer:
    def __init__(
        self,
        target_dir_path: Path,
        configs_dir_path: Path,
        state_file_path: Path,
        default_policy: Policy,
        specific_policies: dict[str, Policy],
    ):
        self.target_dir_path = target_dir_path
        self.configs_dir_path = configs_dir_path
        self.state_file_path = state_file_path
        self.sync_state = self._load_sync_state()

        self.exclude_patterns = EXCLUDE_PATTERNS
        self.default_policy = default_policy
        self.specific_policies = specific_policies

    def _load_sync_state(self) -> dict[str, dict[str, Any]]:
        if not self.state_file_path.exists():
            return {}
        with self.state_file_path.open("r") as f:
            return json.load(f)

    def _save_sync_state(self):
        with self.state_file_path.open("w") as f:
            json.dump(self.sync_state, f, indent=4)

    def show_sync_state(self):
        """Read and display the current sync states."""
        if not self.sync_state:
            print("There is no sync state available.")
            return

        print("Current Sync States:")
        for file_path, state_info in self.sync_state.items():
            print(f"{file_path}:")
            print(json.dumps(state_info, indent=4))

    def clear_sync_state(self):
        """Clear all sync states."""
        if not self.sync_state:
            print("There is no sync state to clear.")
            return
        self.sync_state = {}
        self._save_sync_state()
        print("All sync states have been cleared.")

    def _prompt_for_confirmation(self, message: str) -> bool:
        response = input(message).strip().lower()
        return response in ["y", "yes"]

    def _sync_by_policy(
        self,
        source_file: Path,
        target_file: Path,
        tmp_target_file: Path,
        policy: Policy,
        force=False,
    ) -> bool:
        """
        Sync existing file according to given policy. Create new file if the target does not exist.

        The actual target is a tmp file. It is expected that the caller will move
        the tmp file to the target location in an appropriate way.

        Throws exception on failure.

        Args:
            source_file (Path): The source file path.
            target_file (Path): The target file path.
            policy (Policy): The sync policy (append or overwrite).
            tmp_suffix (str, optional): Suffix for the temporary file. Defaults to ".tmp_sync".
            force (bool, optional): If True, skip confirmation prompts. Defaults to False.

        Returns:
            bool: True on success, False on user-aborted operation.
        """
        target_file.parent.mkdir(parents=True, exist_ok=True)

        append_text = source_file.read_text(encoding="utf-8")
        if target_file.exists():
            if not force and not self._prompt_for_confirmation(
                f"{policy.capitalize()} to existing file: {target_file}? (y/n): "
            ):
                print(f"Skipping {policy.lower()} operation.")
                return False

            match policy:
                case Policy.APPEND:
                    origin_text = target_file.read_text(encoding="utf-8")
                    tmp_target_file.write_text(origin_text + "\n\n" + append_text)
                case Policy.OVERWRITE:
                    tmp_target_file.write_text(append_text, encoding="utf-8")
                case Policy.PREPEND_SOURCE_STATEMENT:
                    origin_lines = target_file.open("r", encoding="utf-8").readlines()
                    expected_statement = f'source "{source_file}"\n'
                    if len(origin_lines) < 2 or origin_lines[1] != expected_statement:
                        origin_text = "".join(origin_lines)
                        source_statement = (
                            f'# Source personal configs\nsource "{source_file}"'
                        )
                        tmp_target_file.write_text(
                            source_statement + "\n\n" + origin_text, encoding="utf-8"
                        )

        else:
            if not force and not self._prompt_for_confirmation(
                f"Target file does not exist. Create {target_file} and copy content? (y/n): "
            ):
                print(f"Skipping {policy.lower()} operation.")
                return False

            match policy:
                case Policy.PREPEND_SOURCE_STATEMENT:
                    source_statement = (
                        f'# Source personal configs\nsource "{source_file}"'
                    )
                    append_text = source_statement
                case _:
                    pass

            tmp_target_file.write_text(append_text, encoding="utf-8")

        print(f"Successfully {policy.lower()} to {target_file}")
        return True

    def sync(self, source_files: list[Path], force=False) -> int:
        """
        Sync files and update sync states.
        It is an atomic operation. If any error occurs on syncing,
        all changes will be rolled back, and no sync state will be updated.

        Args:
            source_files (list[Path]): List of source file paths to sync.
            force (bool, optional): If True, skip confirmation prompts. Defaults to False.

        Returns:
            int: 0 on success, non-zero on failure.
        """
        source_files = source_files
        target_files = [
            self.target_dir_path / f.relative_to(self.configs_dir_path)
            for f in source_files
        ]
        tmp_target_files = [
            target_file.with_suffix(target_file.suffix + ".tmp_sync")
            for target_file in target_files
        ]

        synced = {f: False for f in source_files}

        try:
            for source, target, tmp_target in zip(
                source_files, target_files, tmp_target_files
            ):
                policy = self.specific_policies.get(
                    str(source.relative_to(self.configs_dir_path)), self.default_policy
                )

                synced[source] = self._sync_by_policy(
                    source_file=source,
                    target_file=target,
                    tmp_target_file=tmp_target,
                    policy=policy,
                    force=force,
                )

            # If all syncing operations succeed, rename tmp files to actual target files
            for target, tmp_target in zip(target_files, tmp_target_files):
                if tmp_target.exists():
                    tmp_target.rename(target)

            print("Successfully finished syncing.")
            # Save updated sync states
            updated_sync_states = {
                str(f): self.sync_state[str(f)] for f in source_files if synced[f]
            }
            self.sync_state = self._load_sync_state()
            self.sync_state.update(updated_sync_states)
            self._save_sync_state()
            print(f"Updated Sync States: {json.dumps(updated_sync_states, indent=4)}")
            return 0
        except Exception as e:
            print(f"Error during syncing: {e}, sync aborted. Changes rolled back.")
            return 1
        finally:
            # Clean up temporary files
            for tmp_target in tmp_target_files:
                if tmp_target.exists():
                    tmp_target.unlink()

    def _compute_file_hash(self, file_path):
        with file_path.open("rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _validate_expected_condition(
        self, source_path: Path, target_path: Path
    ) -> bool:
        """
        For other policies, validate file hash match between source and target.
        For PREPEND_SOURCE_STATEMENT policy, validate whether target file contains the source statement.
        """
        policy = self.specific_policies.get(
            str(source_path.relative_to(self.configs_dir_path)), self.default_policy
        )

        match policy:
            case Policy.PREPEND_SOURCE_STATEMENT:
                expected_statement = f'source "{source_path}"\n'
                target_lines = target_path.open("r", encoding="utf-8").readlines()
                return target_lines[1] == expected_statement
            case _:
                source_hash = self._compute_file_hash(source_path)
                target_hash = self._compute_file_hash(target_path)
                return source_hash == target_hash

    def _validate_exclude(self, source_path: Path) -> bool:
        """
        Return True if the file_path should be excluded based on:
        1. predefined exclude patterns
        2. current sync states

        When checking sync states, if the file is considered out of sync (i.e., source file is modified or
        target file is deleted since the last sync), the self.sync_state will be updated.
        """
        relative_path = source_path.relative_to(self.configs_dir_path)

        # Check exclude patterns exclusion
        for pattern in self.exclude_patterns:
            if pattern.endswith("/"):
                if any(str(part) == pattern[:-1] for part in relative_path.parents):
                    return True
            else:
                if relative_path.match(pattern):
                    return True

        # Check sync state exclusion
        timestamp = datetime.now().isoformat()
        previous_hash = self.sync_state.get(str(source_path), {}).get("hash")
        current_hash = self._compute_file_hash(source_path)

        # If new file (not in sync state), need to sync
        if str(source_path) not in self.sync_state:
            self.sync_state[str(source_path)] = {}
            self.sync_state[str(source_path)]["hash"] = current_hash
            self.sync_state[str(source_path)]["last sync timestamp"] = timestamp
            self.sync_state[str(source_path)]["sync reason"] = "New file to be synced"
            return False

        # If source file is modified since last sync, need to sync
        if previous_hash != current_hash:
            self.sync_state[str(source_path)]["hash"] = current_hash
            self.sync_state[str(source_path)]["last sync timestamp"] = timestamp
            self.sync_state[str(source_path)]["sync reason"] = (
                "Source File is modified (hash mismatch) since last sync"
            )
            return False

        # If target file does not exist or is deleted since last sync, need to sync
        target_path = self.target_dir_path / relative_path
        if not target_path.exists():
            self.sync_state[str(source_path)]["last sync timestamp"] = timestamp
            self.sync_state[str(source_path)]["sync reason"] = (
                "Target file dose not exist or is deleted since last sync"
            )
            return False

        # If target file does meet the expected condition, need to sync
        if not self._validate_expected_condition(source_path, target_path):
            self.sync_state[str(source_path)]["last sync timestamp"] = timestamp
            self.sync_state[str(source_path)]["sync reason"] = (
                "Target file does not meet the expected condition"
            )
            return False

        return True

    def get_syncing_files(self) -> list[Path]:
        """
        Get all files that need to be synced, excluding those that match exclude patterns
        or are considered up-to-date based on sync states.

        Returns:
            list[Path]: List of file paths to be synced.
        """
        syncing_files = []

        for file_path in self.configs_dir_path.rglob("*"):
            if not file_path.is_file():
                continue
            if self._validate_exclude(file_path):
                continue

            syncing_files.append(file_path)

        return syncing_files


def validation_check(configs_dir_path: Path) -> bool:
    """Validate that the script is run from the configs directory."""
    if not configs_dir_path.exists() or not configs_dir_path.is_dir():
        print(
            f"ERROR: Configs path {configs_dir_path} does not exist or is not a directory."
        )
        return False
    elif Path.cwd() != configs_dir_path:
        print(
            f"ERROR: This script must be run from {configs_dir_path}, current directory is {Path.cwd()}."
        )
        return False

    return True


if __name__ == "__main__":
    args = parse_arguments()

    TARGET_DIR_PATH = Path.cwd() / "debug_home" if args.debug else Path.home()
    CONFIGS_DIR_PATH = Path.home() / "configs"
    STATE_FILE_PATH = CONFIGS_DIR_PATH / ".sync_state.json"

    print(f"Target directory: {TARGET_DIR_PATH}")
    print(f"Source directory: {CONFIGS_DIR_PATH}")
    print(f"State file: {STATE_FILE_PATH}")

    if not validation_check(CONFIGS_DIR_PATH):
        sys.exit(1)

    if args.overwrite:
        DEFAULT_POLICY = Policy.OVERWRITE
    elif args.append:
        DEFAULT_POLICY = Policy.APPEND

    SPECIFIC_POLICIES = {
        ".bashrc": Policy.PREPEND_SOURCE_STATEMENT,
        ".zshrc": Policy.PREPEND_SOURCE_STATEMENT,
    }

    syncer = ConfigSyncer(
        TARGET_DIR_PATH,
        CONFIGS_DIR_PATH,
        STATE_FILE_PATH,
        DEFAULT_POLICY,
        SPECIFIC_POLICIES,
    )

    if args.show_state:
        syncer.show_sync_state()
        sys.exit(0)

    if args.clear_state:
        syncer.clear_sync_state()
        sys.exit(0)

    syncing_files = syncer.get_syncing_files()
    print(f"Found {len(syncing_files)} files to consider for syncing:")
    for f in syncing_files:
        print(f)

    sys.exit(syncer.sync(syncing_files, force=args.force))
