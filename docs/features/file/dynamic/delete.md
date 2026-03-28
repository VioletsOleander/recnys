# Delete

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo.template": <<any>> }
```

In current execution, the `foo.template` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo.template` from last execution does not exist.
