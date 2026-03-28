# Copy

## 1. Destination not specified

**Scenario**: Render and sync file to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `~/foo` exists with the content rendered from `foo.template` with variables defined in `variables.yaml`

## 2. Destination specified

**Scenario**: Render and sync file to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { dest: { <os>: "bar" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: `~/bar` exists with the content rendered from `foo.template` with variables defined in `variables.yaml`

**Scenario**: Skip render and sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo.template": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`

_Expectation_: No-op
