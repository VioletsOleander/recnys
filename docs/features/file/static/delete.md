# Delete

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo": <<any>> }
```

In current execution, the `foo` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo` from last execution does not exist.
