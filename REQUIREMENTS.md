# Requirements

This document captures the requirements for Recnys in a structured format.
Each requirement has a unique ID, a clear description, and acceptance criteria that map
directly to unit tests. New features should be added here before implementation.

## Format

Each requirement entry follows this template:

```
### REQ-{MODULE}-{NUMBER}: {Short Title}

**Status**: Implemented | Planned

**Description**: {What the system must do}

**Acceptance Criteria**:
- {Specific, testable condition}
- ...
```

---

## CFG – Configuration Loading

### REQ-CFG-1: Load configuration from `recnys.yaml`

**Status**: Implemented

**Description**: The system must load the dotfile synchronization configuration from a
`recnys.yaml` file located in the current working directory.

**Acceptance Criteria**:
- Given a valid `recnys.yaml` in the current working directory, `load_config` returns
  its contents as a dictionary.
- Given no `recnys.yaml` in the current working directory, `load_config` raises
  `FileNotFoundError`.

### REQ-CFG-2: Load variables from `variables.yaml`

**Status**: Implemented

**Description**: When template files are present, the system must load Jinja2 template
variables from a `variables.yaml` file in the current working directory.

**Acceptance Criteria**:
- Given a valid `variables.yaml`, `load_variables` returns its contents as a flat
  string-to-string dictionary.
- Given no `variables.yaml`, `load_variables` raises `FileNotFoundError`.

---

## CANON – Configuration Canonicalization

### REQ-CANON-1: Resolve platform-specific destination paths

**Status**: Implemented

**Description**: The canonicalizer must select the destination path for the current
operating system. Only `Linux` and `Windows` are supported platforms.

**Acceptance Criteria**:
- When a `dest` block contains a key for the current platform, that path (relative to
  `~`) is used as the destination.
- When a `dest` block contains an empty string for the current platform, the
  destination is `None` (no syncing on that platform).
- When a `dest` block omits the current platform, the default destination path is used.
- When running on an unsupported platform, the canonicalizer raises `RuntimeError`.

### REQ-CANON-2: Derive default destination paths

**Status**: Implemented

**Description**: When no explicit destination is provided for a file, the canonicalizer
must derive a sensible default based on the source path and current platform.

**Acceptance Criteria**:
- A top-level file (e.g. `.vimrc`) defaults to `~/.vimrc` on Linux and `~\.vimrc` on
  Windows.
- A file under a subdirectory (e.g. `nvim/init.lua`) defaults to
  `~/.config/nvim/init.lua` on Linux and `~\AppData\Roaming\nvim\init.lua` on Windows.

### REQ-CANON-3: Expand directory entries

**Status**: Implemented

**Description**: A configuration entry whose key ends with `/` must be expanded into
one entry per file found recursively inside that directory. Each expanded entry inherits
the policy of the parent directory entry, and the destination is derived relative to
the parent directory destination.

**Acceptance Criteria**:
- Given a directory entry `nvim/` with destination `~/.config/nvim/`, each file
  `nvim/foo/bar.txt` produces an entry with destination `~/.config/nvim/foo/bar.txt`.
- When the directory entry has destination `None`, all expanded entries also have
  destination `None`.

### REQ-CANON-4: Resolve later entries taking precedence over earlier ones

**Status**: Implemented

**Description**: When a more specific entry (e.g. `nvim/init.lua`) appears after a
directory entry (e.g. `nvim/`), the specific entry's destination and policy override
those derived from the directory expansion.

**Acceptance Criteria**:
- Given `nvim/` followed by `nvim/init.lua` with a different destination, the resulting
  canonical entry for `nvim/init.lua` uses the destination from the explicit entry.

### REQ-CANON-5: Handle `.template` suffix in source and destination paths

**Status**: Implemented

**Description**: Source files ending in `.template` are rendered before syncing. The
canonicalizer must:
1. Set the sync source to the rendered output path (stripping `.template`).
2. Record a render specification pointing from the original template to the rendered
   output path.

**Acceptance Criteria**:
- For a key `.bashrc.template`, the sync source is
  `<rendered_file_dir>/.bashrc` (the rendered output).
- For a key `.bashrc.template`, a render spec is created with `src` equal to the
  original template file and `dst` equal to `<rendered_file_dir>/.bashrc`.
- When the template entry has destination `None`, the render spec destination is also
  `None` (no rendering needed).

---

## RENDER – Template Rendering

### REQ-RENDER-1: Render Jinja2 templates using loaded variables

**Status**: Implemented

**Description**: Each `TemplateRenderTask` must be executed by reading the template
file, substituting the loaded variables using Jinja2, and writing the rendered output
to the task's destination path.

**Acceptance Criteria**:
- Given a template file containing `{{ variable }}` and a variables dictionary with
  `variable: value`, the rendered output file contains `value`.
- The destination's parent directories are created if they do not exist.
- On a rendering error, the task result is `Failure` and no partial output file is left
  behind.

### REQ-RENDER-2: Skip rendering when the template file is unchanged

**Status**: Implemented

**Description**: If the template source file has not been modified since the last
successful render and the rendered output file still exists and is up-to-date, the
render task must be skipped.

**Acceptance Criteria**:
- When the source hash matches the last recorded hash and the destination file exists
  and is identical to the source, the render task result is `Skipped`.

---

## SYNC – File Synchronization

### REQ-SYNC-1: Sync a file using the `copy` policy

**Status**: Implemented

**Description**: When the sync policy is `copy`, the system must write the exact
contents of the source file to the destination path, replacing any existing content.

**Acceptance Criteria**:
- After a `copy` sync, the destination file contains the same text as the source file.
- The destination's parent directories are created if they do not exist.
- On a copy error, the task result is `Failure` and no partial output file is left
  behind.

### REQ-SYNC-2: Sync a file using the `source` policy

**Status**: Implemented

**Description**: When the sync policy is `source`, the system must prepend a
`source "<src_path>"` statement to the beginning of the destination file, preserving
any existing content that follows it.

**Acceptance Criteria**:
- After a `source` sync to a non-existent destination, the destination contains only
  the `source` statement followed by a blank line.
- After a `source` sync to an existing destination, the `source` statement appears at
  the top, followed by the original content of the destination.

### REQ-SYNC-3: Prompt the user for confirmation before syncing

**Status**: Implemented

**Description**: Before overwriting or creating a destination file, the system must
prompt the user for confirmation unless `--skip-confirmation` is given.

**Acceptance Criteria**:
- When `skip=False` and the user declines the prompt, the task result is `Skipped`.
- When `skip=True`, no prompt is shown and the sync proceeds without user interaction.

### REQ-SYNC-4: Skip syncing when the source and destination are unchanged

**Status**: Implemented

**Description**: If the source file has not changed since the last successful sync and
the destination file still exists and matches the source, the sync task must be skipped
automatically.

**Acceptance Criteria**:
- When the source hash matches the last recorded hash and the destination file exists
  and is identical to the source, the sync task result is `Skipped`.

---

## EXEC – Execution Decision Making

### REQ-EXEC-1: Execute the task when there is no previous execution record

**Status**: Implemented

**Description**: A file I/O task must always be executed when there is no prior
execution record for it, because the destination file may not exist yet.

**Acceptance Criteria**:
- When `last_task_record` is `None`, the execution decision is `ok=True`.

### REQ-EXEC-2: Execute the task when the destination file is missing

**Status**: Implemented

**Description**: Even when a previous execution record exists, the task must be
re-executed if the destination file is absent.

**Acceptance Criteria**:
- When `last_task_record` is present but `task.dst` does not exist, the execution
  decision is `ok=True`.

### REQ-EXEC-3: Execute the task when the source file has changed

**Status**: Implemented

**Description**: When the source file's content hash differs from the hash stored in
the last execution record, the task must be re-executed.

**Acceptance Criteria**:
- When the current hash of `task.src` differs from `last_task_record.file_hash`,
  the execution decision is `ok=True`.

### REQ-EXEC-4: Execute the task when the destination file has drifted from the source

**Status**: Implemented

**Description**: When the destination file exists and its content has been changed
externally (i.e. it no longer matches the source), the task must be re-executed.

**Acceptance Criteria**:
- When `hash(task.src) == last_task_record.file_hash` but `hash(task.dst) != hash(task.src)`,
  the execution decision is `ok=True`.

### REQ-EXEC-5: Skip the task when source and destination are both unchanged

**Status**: Implemented

**Description**: When the source file hash matches the last recorded hash and the
destination content matches the source, the task must be skipped.

**Acceptance Criteria**:
- When `hash(task.src) == last_task_record.file_hash` and `hash(task.dst) == hash(task.src)`,
  the execution decision is `ok=False`.

### REQ-EXEC-6: Force execute the task when `force_execute` is set

**Status**: Implemented

**Description**: When `task.force_execute` is `True`, all other conditions must be
ignored and the task must always be executed.

**Acceptance Criteria**:
- When `task.force_execute` is `True`, the execution decision is `ok=True` regardless
  of the last execution record or file states.

### REQ-EXEC-7: Execute the task when the configuration entry has changed

**Status**: Planned

**Description**: When a configuration entry (e.g. its `policy` or `dest`) has been
modified since the last execution, the task must be re-executed to reflect the new
configuration, even if the source file itself is unchanged.

**Acceptance Criteria**:
- When the sync policy in the current configuration differs from the policy recorded at
  the time of the last execution, the execution decision is `ok=True`.
- When the destination path in the current configuration differs from the destination
  recorded at the time of the last execution, the execution decision is `ok=True`.

**Notes**: Implementing this requirement likely requires extending `TaskExecutionRecord`
to store the configuration snapshot (policy, destination) used at execution time, and
comparing it against the current task configuration in `_make_execution_decision`. This
may require changes to `FileIOTask`, `FileSyncTask`, `TaskExecutionRecord`, and
`FileIOTaskExecutor`.

---

## RECORD – Execution Record Management

### REQ-RECORD-1: Persist execution records to a JSON file

**Status**: Implemented

**Description**: After each execution run, the full execution record must be saved to a
JSON file so it can be used to make decisions in subsequent runs.

**Acceptance Criteria**:
- After calling `ExecutionRecord.save(file_path)`, a valid JSON file exists at
  `file_path` that contains all task records from that execution.

### REQ-RECORD-2: Load execution records from a JSON file

**Status**: Implemented

**Description**: At the start of each run, the system must load the execution record
from the previously saved JSON file.

**Acceptance Criteria**:
- `ExecutionRecord.from_json(file_path)` returns the records previously saved by
  `ExecutionRecord.save`.
- When the file does not exist, `ExecutionRecord.from_json` returns an empty record
  (not an error).

---

## CLI – Command-Line Interface

### REQ-CLI-1: Skip confirmation prompts with `-s` / `--skip-confirmation`

**Status**: Implemented

**Description**: The `--skip-confirmation` flag must disable all per-file user
confirmation prompts during a sync run.

**Acceptance Criteria**:
- When the flag is provided, no prompt is displayed and all applicable sync tasks are
  executed without user input.

### REQ-CLI-2: Enable verbose logging with `-v` / `--verbose`

**Status**: Implemented

**Description**: The `--verbose` flag must set the logging level to `DEBUG`, revealing
detailed internal execution steps.

**Acceptance Criteria**:
- When the flag is provided, the root logger level is `DEBUG`.

### REQ-CLI-3: Force re-render all templates with `-r` / `--force-render`

**Status**: Implemented

**Description**: The `--force-render` flag must cause all render tasks to be executed
regardless of any cached execution records.

**Acceptance Criteria**:
- When the flag is provided, `build_render_tasks` produces tasks with
  `force_execute=True`.

### REQ-CLI-4: Force re-sync all files with `-c` / `--force-sync`

**Status**: Implemented

**Description**: The `--force-sync` flag must cause all sync tasks to be executed
regardless of any cached execution records.

**Acceptance Criteria**:
- When the flag is provided, `build_sync_tasks` produces tasks with
  `force_execute=True`.

### REQ-CLI-5: Render only (no sync) with `-o` / `--render-only`

**Status**: Implemented

**Description**: The `--render-only` flag must cause the program to exit after
completing the render phase, skipping file synchronization entirely.

**Acceptance Criteria**:
- When the flag is provided, no sync tasks are executed and the program exits with
  status `0` after rendering.

### REQ-CLI-6: Clean cached data with `--clean`

**Status**: Implemented

**Description**: The `--clean` flag must remove the `.recnys` project data directory
(which contains rendered files and execution records) and then exit without performing
any render or sync operations.

**Acceptance Criteria**:
- When the flag is provided and `.recnys` exists, the directory is deleted and the
  program exits with status `0`.
- No render or sync tasks are executed when `--clean` is provided.
