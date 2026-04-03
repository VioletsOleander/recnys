# Static File

## 1. Root File

**Requirement**: `foo` exists in the repository root.

### 1.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo` exists as a symlink to `foo`

### 1.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "bar" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/bar` exists as a symlink to `foo`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op

## 2. Leaf File

**Requirement**: `foo/bar` exists in the repository root.

### 2.1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/foo/bar` exists as a symlink to `foo/bar`

### 2.2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { dest: { <os>: "foo/baz" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo/baz` exists as a symlink to `foo/bar`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
