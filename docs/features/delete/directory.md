# Directory

**Requirement**:

- `<<directory>>/` exists in the repository root.
- `variables.yaml` is defined in repository root, if there is any dynamic file under the directory or its subdirectories.

**Scenario**: Delete artifact on entry remove or change

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "<<directory>>": <<any>> }
```

In current execution, the `<<directory>>` entry does not exist, or still exists but with different content.

_Operation_: Run `recnys`

_Expectation_: Artifact of `<<directory>>` from last execution does not exist.

**Scenario**: Delete artifact on files/subdirectories deletion under `copy` policy

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "<<directory>>": { <<any>>, policy: "copy" } }
```

In current execution, the `<<directory>>` entry still exists with the same content.

Compared to last execution, some files and/or subdirectories under `<<directory>>` and/or its subdirectories have been deleted.

_Operation_: Run `recnys`

_Expectation_: Artifact of every deleted file and/or subdirectory from last execution does not exist.

**Scenario**: Delete artifact on dynamic files deletion under `symlink` policy

_Condition_: In last execution, the content of `recnys.yaml` is:

```yaml
{ "<<directory>>": <<any>> }
```

with policy resolved to `symlink`.

In current execution, the `<<directory>>` entry still exists with the same content.

Compared to last execution, some dynamic files under `<<directory>>` and/or its subdirectories have been deleted.

_Operation_: Run `recnys`

_Expectation_: Artifact of every deleted dynamic file from last execution does not exist.
