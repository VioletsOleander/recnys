# Directory

**Requirement**: `<<directory>>` exists in the repository root.

## 1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/<config_directory>/<<directory>>` exists as a symlink to `<<directory>>`

## 2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { dest: { <os>: "foo/" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `<home>/foo/` exists as a symlink to `<<directory>>`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
