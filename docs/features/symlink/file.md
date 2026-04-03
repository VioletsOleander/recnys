# File

## 1. Root File

**Requirement**: `<<root_file>>` exists in the repository root, and it is a static file.

### 1.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<<root_file>>` exists as a symlink to `<<root_file>>`

### 1.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { dest: { <os>: "foo" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo` exists as a symlink to `<<root_file>>`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Leaf File

**Requirement**: `<<leaf_file>>` exists in the repository root, and it is a static file.

### 2.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/<<leaf_file>>` exists as a symlink to `<<leaf_file>>`

### 2.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { dest: { <os>: "foo/bar" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo/bar` exists as a symlink to `<<leaf_file>>`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
