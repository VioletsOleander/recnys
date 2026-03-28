# Delete

## 1. Directory contains static files only

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>> }
```

In current execution, the `foo/` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo/` from last execution does not exist.

## 2. Directory contains dynamic files

**Requirement**: `variables.yaml` is defined in repository root.

### 2.1 `recnys.yaml` entry

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>> }
```

In current execution, the `foo/` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `foo/` from last execution does not exist.

### 2.2 `variables.yaml` file

**Scenario**: Delete (sub)artifact on variables change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>> }
```

In current execution, the `foo/` entry still exists with the same content.

Compared to last execution, the hash value of `variables.yaml` has changed.

_Operation_: Run `recnys`

_Expectation_:

- Artifacts of subdirectories that contain dynamic files only do not exist.
- Artifacts of subdirectories that contain static files and dynamic files partially exist, i.e. the artifacts of static files under the subdirectories still exist while the artifacts of dynamic files under the subdirectories do not exist.
