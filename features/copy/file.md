# Normal File

**Requirement**:

- `recnys.yaml` exists in repository root.
- `foo` exists in the repository root.

## 1. Destination not specified

**Scenario**: Sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: `~/foo` exists with the same content as `foo`

## 2. Destination specified

```python
# Define `<os>` as:
match platform.system():
    "Windows": os = "Windows"
    "Linux": os = "Linux"
```

**Scenario**: Sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "bar" }, policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: `~/bar` exists with the same content as `foo`

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: No-op
