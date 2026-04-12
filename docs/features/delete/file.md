# File

**Requirement**: `<<file>>` exists in the repository root.

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "<<file>>": <<any>> }
```

In current execution, the `<<file>>` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `<<file>>` from last execution does not exist.
