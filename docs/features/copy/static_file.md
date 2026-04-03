# Static File

## 1. Root File

**Requirement**: `foo` exists in the repository root.

### 1.1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo` exists with the same content as `foo`

### 1.2. Destination specified

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "bar" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/bar` exists with the same content as `foo`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Leaf File

**Requirement**: `foo/bar` exists in the repository root.

### 2.1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/bar` exists with the same content as `foo/bar`

### 2.2. Destination specified

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { dest: { <os>: "foo/baz" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/baz` exists with the same content as `foo/bar`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
