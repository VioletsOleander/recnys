from collections.abc import Generator
from pathlib import Path

from recnys.parsing.model import EntryKey, EntryValue, KeyCategory, ParsedConfig
from recnys.scanning.model import Policy

from .model import (
    CreateOperation,
    CreateOperationCode,
    DeleteOperation,
    DeleteOperationCode,
    Operation,
)


class ConfigLowerer:
    home: Path
    repo: Path

    def __init__(self, home: Path, repo: Path) -> None:
        self.home = home
        self.repo = repo

    def lower(self, config: ParsedConfig, last_config: ParsedConfig) -> Generator[Operation]:
        prev_config = last_config.root
        curr_config = config.root

        for key, value in prev_config.items():
            if key in curr_config and curr_config[key] == value:
                operation = self._lower_unchanged_entry(key=key, value=value)
            else:
                operation = self._lower_changed_entry(prev_key=key, prev_value=value)

            if operation is not None:
                yield operation

        for key, value in curr_config.items():
            if key in prev_config:
                continue

            yield self._lower_added_entry(curr_key=key, curr_value=value)

    def _lower_unchanged_entry(self, key: EntryKey, value: EntryValue) -> Operation | None:
        pass

    def _lower_changed_entry(self, prev_key: EntryKey, prev_value: EntryValue) -> DeleteOperation:
        if prev_value.policy == Policy.SYMLINK:
            code = DeleteOperationCode.UNLINK
        else:
            code = (
                DeleteOperationCode.RMFILE
                if prev_key.category == KeyCategory.FILE
                else DeleteOperationCode.RMDIR
            )

        return DeleteOperation(dest=self.repo / prev_key.src, code=code)

    def _lower_added_entry(self, curr_key: EntryKey, curr_value: EntryValue) -> CreateOperation:
        if curr_value.policy == Policy.SYMLINK:
            code = CreateOperationCode.SYMLINK
        else:
            code = (
                CreateOperationCode.COPY
                if curr_key.attribute.static
                else CreateOperationCode.RENDER
            )

        return CreateOperation(
            src=self.repo / curr_key.src, dest=self.home / curr_value.dest, code=code
        )
