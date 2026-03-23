# Copy

**Requirement**: `variables.yaml` is defined in repository root, if there is any dynamic file under the directory or its subdirectories.

## 1. Destination not specified

**Scenario**: Sync files under directory to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `<default_directory>`.

## 2. Destination specified

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/bar/`.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
