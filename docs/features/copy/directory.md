# Directory

**Requirement**:

- `<<directory>>` exists in the repository root.
- `variables.yaml` is defined in repository root, if `<<directory>>` is a dynamic directory.

## 1. Destination not specified

**Scenario**: Sync files under directory to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: Every file under `<<directory>>` and its subdirectories has its counterpart file under `<config_directory>/<<directory>>`.

## 2. Destination specified

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { dest: { <os>: "foo/" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: Every file under `<<directory>>` and its subdirectories has its counterpart file under `<home>/foo/`.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
