# Dynamic File

**Requirement**: `variables.yaml` exists in repository root.

## 1. Root File

**Requirement**: `foo.template` exists in the repository root.

### 1.1. Destination not specified

**Scenario**: Render and sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo` exists with the content rendered from `foo.template` with variables defined in `variables.yaml`

### 1.2. Destination specified

**Scenario**: Render and sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { dest: { <os>: "bar" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/bar` exists with the content rendered from `foo.template` with variables defined in `variables.yaml`

**Scenario**: Skip render and sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Leaf File

**Requirement**: `foo/bar.template` exists in the repository root.

### 2.1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar.template": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/bar` exists with content rendered from `foo/bar.template` with variables defined in `variables.yaml`

### 2.2. Destination specified

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar.template": { dest: { <os>: "foo/baz" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/baz` exists with content rendered from `foo/bar.template` with variables defined in `variables.yaml`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar.template": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
