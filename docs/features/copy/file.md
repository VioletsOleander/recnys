# File

**Requirement**: `variables.yaml` exists in repository root, if `<<root_file>>` or `<<leaf_file>>` is dynamic file.

## 1. Root File

**Requirement**: `<<root_file>>` exists in the repository root.

### 1.1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<config_directory>/<<root_file>>` exists, containing the counterpart content of `<<root_file>>`

### 1.2. Destination specified

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { dest: { <os>: "foo" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo` exists, containing the counterpart content of `<<root_file>>`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<root_file>>": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Leaf File

**Requirement**: `<<leaf_file>>` exists in the repository root.

### 2.1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<config_directory>/<<leaf_file>>` exists, containing the counterpart content of `<<leaf_file>>`

### 2.2. Destination specified

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { dest: { <os>: "foo/bar" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo/bar` exists, containing the counterpart content of `<<leaf_file>>`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<leaf_file>>": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
