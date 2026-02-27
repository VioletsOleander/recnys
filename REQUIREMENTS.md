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
- {Specific, testable condition expressed as observable behavior}
- ...
```

---

## CFG – Configuration Loading

### REQ-CFG-1: Load configuration from `recnys.yaml`

**Status**: Implemented

**Description**: The system must load the dotfile synchronization configuration from a
`recnys.yaml` file located in the current working directory.

**Acceptance Criteria**:
- Given a valid `recnys.yaml` in the current working directory, the configuration is
  successfully read and used to determine sync targets.
- Given no `recnys.yaml` in the current working directory, the program exits with an
  error indicating the file was not found.

### REQ-CFG-2: Load variables from `variables.yaml`

**Status**: Implemented

**Description**: When template files are present, the system must load template
variables from a `variables.yaml` file in the current working directory.

**Acceptance Criteria**:
- Given a valid `variables.yaml`, the variables it defines are available for template
  rendering.
- Given no `variables.yaml`, the program exits with an error indicating the file was
  not found.

---

## CANON – Configuration Canonicalization

### REQ-CANON-1: Resolve platform-specific destination paths

**Status**: Implemented

**Description**: The system must select the destination path appropriate for the current
operating system. Only `Linux` and `Windows` are supported platforms.

**Acceptance Criteria**:
- When a `dest` block specifies a path for the current platform, that path is used as
  the destination.
- When a `dest` block specifies an empty string for the current platform, the file is
  not synced on that platform.
- When a `dest` block omits the current platform, the default destination path is used.
- When running on an unsupported platform, the program exits with an error.

### REQ-CANON-2: Derive default destination paths

**Status**: Implemented

**Description**: When no explicit destination is provided for a file, the system must
derive a sensible default destination based on the source path and current platform.

**Acceptance Criteria**:
- A top-level file (e.g. `.vimrc`) defaults to `~/.vimrc` on Linux and `~\.vimrc` on
  Windows.
- A file under a subdirectory (e.g. `nvim/init.lua`) defaults to
  `~/.config/nvim/init.lua` on Linux and `~\AppData\Roaming\nvim\init.lua` on Windows.

### REQ-CANON-3: Expand directory entries

**Status**: Implemented

**Description**: A configuration entry whose key ends with `/` must be expanded into
one entry per file found recursively inside that directory. Each expanded entry inherits
the policy of the parent directory entry, and its destination is derived relative to
the parent directory destination.

**Acceptance Criteria**:
- Given a directory entry `nvim/` with destination `~/.config/nvim/`, each file
  `nvim/foo/bar.txt` is synced to `~/.config/nvim/foo/bar.txt`.
- When the directory entry specifies no syncing for the current platform, none of the
  files inside that directory are synced.

### REQ-CANON-4: Later entries override earlier ones for the same file

**Status**: Implemented

**Description**: When a more specific entry (e.g. `nvim/init.lua`) appears after a
directory entry (e.g. `nvim/`), the specific entry's destination and policy override
those derived from the directory expansion.

**Acceptance Criteria**:
- Given `nvim/` followed by `nvim/init.lua` with a different destination, `nvim/init.lua`
  is synced to the destination from the explicit entry, not the one inherited from `nvim/`.

### REQ-CANON-5: Template files are rendered before syncing

**Status**: Implemented

**Description**: Source files ending in `.template` must be rendered into a concrete
file first, and that rendered output must then be synced to the destination. The
original `.template` file is never synced directly.

**Acceptance Criteria**:
- A template file (e.g. `.bashrc.template`) is rendered and the rendered output
  (`.bashrc`) is what is synced to the destination, not the raw `.template` file.
- When a template entry specifies no syncing for the current platform, the template
  file is not rendered either.

---

## RENDER – Template Rendering

### REQ-RENDER-1: Render template files using loaded variables

**Status**: Implemented

**Description**: Each template file must be rendered by substituting the loaded
variables into the template, and the rendered output must be written to an intermediate
location for subsequent syncing.

**Acceptance Criteria**:
- Given a template file containing a variable placeholder and a matching variable
  definition, the rendered output file has the placeholder replaced with the variable
  value.
- The output directory is created automatically if it does not exist.
- On a rendering error, no partial output file is left behind.

### REQ-RENDER-2: Skip rendering when the template file is unchanged

**Status**: Implemented

**Description**: If a template source file has not been modified since the last
successful render and the rendered output still exists, rendering must be skipped.

**Acceptance Criteria**:
- When a template file is re-run without changes, the rendered output file is not
  rewritten.

---

## SYNC – File Synchronization

### REQ-SYNC-1: Sync a file using the `copy` policy

**Status**: Implemented

**Description**: When the sync policy is `copy`, the system must write the exact
contents of the source file to the destination path, replacing any existing content.

**Acceptance Criteria**:
- After a `copy` sync, the destination file contains the same content as the source
  file.
- The destination's parent directories are created if they do not exist.
- On a sync error, no partial output file is left behind.

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
display a prompt and wait for the user to confirm or decline, unless
`--skip-confirmation` is given.

**Acceptance Criteria**:
- When confirmation is required and the user declines, the file is not synced.
- When `--skip-confirmation` is given, no prompt is displayed and the sync proceeds
  without user interaction.

### REQ-SYNC-4: Skip syncing when the source and destination are unchanged

**Status**: Implemented

**Description**: If the source file has not changed since the last successful sync and
the destination file still exists and matches the source, the sync must be skipped
automatically.

**Acceptance Criteria**:
- When a file is re-run without changes to either source or destination, the
  destination file is not rewritten.

---

## EXEC – Execution Decision Making

### REQ-EXEC-1: Execute when there is no previous execution record

**Status**: Implemented

**Description**: A task must always be executed when it has never been run before,
since no destination file will exist yet.

**Acceptance Criteria**:
- When a task has no prior execution history, it is executed and a destination file is
  produced.

### REQ-EXEC-2: Execute when the destination file is missing

**Status**: Implemented

**Description**: Even when a task has been run before, it must be re-executed if the
destination file is absent.

**Acceptance Criteria**:
- When a previously executed task's destination file is deleted, the next run
  re-creates it.

### REQ-EXEC-3: Execute when the source file has changed

**Status**: Implemented

**Description**: When the source file's content has changed since the last execution,
the task must be re-executed so the destination reflects the latest source.

**Acceptance Criteria**:
- When the source file is modified between runs, the destination file is updated in the
  next run.

### REQ-EXEC-4: Execute when the destination file has drifted from the source

**Status**: Implemented

**Description**: When the destination file has been modified externally so that it no
longer matches the source, the task must be re-executed to restore consistency.

**Acceptance Criteria**:
- When the destination file is modified externally between runs (while the source is
  unchanged), the next run overwrites the destination with the current source content.

### REQ-EXEC-5: Skip when source and destination are both unchanged

**Status**: Implemented

**Description**: When both the source file and the destination file are unchanged since
the last execution, the task must be skipped to avoid unnecessary work.

**Acceptance Criteria**:
- When neither the source nor the destination file has changed between runs, the
  destination file is not rewritten.

### REQ-EXEC-6: Force execution regardless of change detection

**Status**: Implemented

**Description**: The user must be able to force all tasks to execute, bypassing all
change-detection logic.

**Acceptance Criteria**:
- When force execution is requested (via `--force-render` or `--force-sync`), all
  applicable tasks are executed even when neither source nor destination has changed.

### REQ-EXEC-7: Execute when the configuration entry has changed

**Status**: Planned

**Description**: When a configuration entry (e.g. its `policy` or `dest`) has been
modified since the last execution, the task must be re-executed to reflect the new
configuration, even if the source file itself is unchanged.

**Acceptance Criteria**:
- When the sync policy for a file is changed in `recnys.yaml` and the program is
  re-run, that file is re-synced using the new policy.
- When the destination path for a file is changed in `recnys.yaml` and the program is
  re-run, the file is synced to the new destination.

---

## RECORD – Execution Record Management

### REQ-RECORD-1: Persist execution history between runs

**Status**: Implemented

**Description**: After each run, the execution history must be saved to disk so that
it is available to inform decisions in subsequent runs.

**Acceptance Criteria**:
- After a successful run, an execution history file exists in the `.recnys` project
  data directory.
- The information saved is sufficient for the system to make correct skip/execute
  decisions on the next run.

### REQ-RECORD-2: Load execution history from a previous run

**Status**: Implemented

**Description**: At the start of each run, the system must read the execution history
saved by the previous run.

**Acceptance Criteria**:
- When an execution history file exists, its contents are used to make
  skip/execute decisions for the current run.
- When no execution history file exists (e.g. first run, or after `--clean`), the
  system starts with an empty history without error.

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

**Description**: The `--verbose` flag must enable detailed diagnostic logging, making
it easier to trace what the program is doing internally.

**Acceptance Criteria**:
- When the flag is provided, detailed diagnostic messages are shown in the output that
  are not visible in the default mode.

### REQ-CLI-3: Force re-render all templates with `-r` / `--force-render`

**Status**: Implemented

**Description**: The `--force-render` flag must cause all template files to be
re-rendered regardless of whether they have changed since the last run.

**Acceptance Criteria**:
- When the flag is provided, all template files are rendered even if their content is
  unchanged since the last run.

### REQ-CLI-4: Force re-sync all files with `-c` / `--force-sync`

**Status**: Implemented

**Description**: The `--force-sync` flag must cause all files to be re-synced
regardless of whether they have changed since the last run.

**Acceptance Criteria**:
- When the flag is provided, all files are synced even if their content is unchanged
  since the last run.

### REQ-CLI-5: Render only (no sync) with `-o` / `--render-only`

**Status**: Implemented

**Description**: The `--render-only` flag must cause the program to exit after
completing the render phase, skipping file synchronization entirely.

**Acceptance Criteria**:
- When the flag is provided, template files are rendered but no files are synced to
  their destinations.

### REQ-CLI-6: Clean cached data with `--clean`

**Status**: Implemented

**Description**: The `--clean` flag must remove the `.recnys` project data directory
(which contains rendered files and execution records) and then exit without performing
any render or sync operations.

**Acceptance Criteria**:
- When the flag is provided, the `.recnys` directory is removed and the program exits
  without syncing or rendering any files.
