# Delete

## 1. `recnys.yaml` entry

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo.template": <<any>> }
```

In current execution, the `foo.template` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo.template` from last execution does not exist.

## 2. `variables.yaml` file

**Scenario**: Delete artifact on variables change

_Condition_: `foo.template` is an entry in `recnys.yaml` in last execution.

Compared to last execution, the hash value of `variables.yaml` has changed.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo.template` from last execution does not exist.
