# Directory

**Requirement**: `foo/` exists in the repository root.

## 1. Directory contains static files only

### 1.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/` exists as a symlink to `foo/`

### 1.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/bar/` exists as a symlink to `foo/`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Directory contains dynamic files

**Requirement**: `variables.yaml` is defined in repository root.

**Comment**: The rendering results of dynamic files are considered as generated files, and do not support symlinks, because symlinks are used primarily for modifying the files from the destination, and it is not expected to modify the rendering results of dynamic files directly.

Whenever we want to modify the rendering results of dynamic files, we should modify the source dynamic files or the variables instead, to maintain a single source of truth and avoid confusion. If we do not keep a single source of truth, the modifications on the rendering results of dynamic files may be overwritten by the next execution of `recnys`, which may cause confusion and unexpected results.

Therefore, for the subdirectories that contain dynamic files, regular directories in counterpart paths will be created, and the rendering results of dynamic files will be **copied** to the counterpart paths, although the policy for the directory is "symlink". This is a special case.

### 2.1. Destination not specified

**Scenario**: Create symlinks and rendering results in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_:

- `<home>/<config_directory>/foo/` exists as a regular directory.
- Counterpart symlinks of subdirectories that contain static files only exist.
- Regular directories in counterpart paths of subdirectories that contain dynamic files exist.
- Counterpart symlinks of static files under subdirectories that contain dynamic files exist.
- Counterpart files of dynamic files under subdirectories that contain dynamic files exist.

### 2.2. Destination specified

**Scenario**: Create symlinks and rendering results in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_:

- `<home>/bar/` exists as a regular directory.
- Counterpart symlinks of subdirectories that contain static files only exist.
- Regular directories in counterpart paths of subdirectories that contain dynamic files exist.
- Counterpart symlinks of static files under subdirectories that contain dynamic files exist.
- Counterpart files of dynamic files under subdirectories that contain dynamic files exist.
