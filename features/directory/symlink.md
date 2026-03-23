# Symlink

## 1. Directory contains static files only

### 1.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<default_directory>` exists as a symlink to `foo/`

### 1.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `~/bar/` exists as a symlink to `foo/`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Directory contains dynamic files

**Requirement**: `variables.yaml` is defined in repository root.

### 2.1. Destination not specified

**Scenario**: Create symlinks and rendering results in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_:

- `<default_directory>` exists as a regular directory.
- Counterpart symlinks of sub-directories that contain static files only exist.
- Regular directories in counterpart paths of sub-directories that contain dynamic files exist.
- Counterpart symlinks of static files under sub-directories that contains dynamic files exist.
- Counterpart files of dynamic files under sub-directories that contains dynamic files exist.

### 2.2. Destination specified

**Scenario**: Create symlinks and rendering results in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_:

- `~/bar/` exists as a regular directory.
- Counterpart symlinks of sub-directories that contain static files only exist.
- Regular directories in counterpart paths of sub-directories that contain dynamic files exist.
- Counterpart symlinks of static files under sub-directories that contains dynamic files exist.
