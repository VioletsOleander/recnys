# Symlink

## 1. Destination not specified

**Scenario**: Make symlink in default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `~/foo` exists as a symlink to `foo`

## 2. Destination specified

**Scenario**: Make symlink in specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "bar" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: `~/bar` exists as a symlink to `foo`

**Scenario**: Skip symlink

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": { dest: { <os>: "" }, policy: "symlink" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
