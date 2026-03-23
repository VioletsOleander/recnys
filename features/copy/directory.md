# Directory

```python
# Define `<os>` as:
match platform.system():
    "Windows": os = "Windows"
    "Linux": os = "Linux"
```

```python
# Define `<default_directory>` as:
match platform.system():
    "Windows": default_directory = "~/AppData/Roaming/foo/"
    "Linux": default_directory = "~/.config/foo/"
```

**Requirement**:

- `recnys.yaml` exists in repository root.
- `foo/` exists in the repository root.

## 1. Directory does not contain template file

**Scenario Background**: There is no template file under `foo/` and its subdirectories.

### 1.1. Destination not specified

**Scenario**: Sync files under directory to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `<default_directory>` with the same content.

### 1.2. Destination specified

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/bar/` with the same content.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "" }, policy: "copy" } }
```

_Operation_: Run `recnys`
_Expectation_: No-op

### 1.2.2. Linux

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { <os>: "bar/" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/.config/bar/` with the same content.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { Linux: "" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: No-op

## 2. Directory contains template file

**Requirement**: `variables.yaml` is defined in repository root.

### 2.1. Destination not specified

#### 2.1.1. Windows

**Scenario**: Sync files under directory or rendered from template files under directory to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "copy" } }
```

where `foo/` is a directory in the repository root, and there is at least one template file under `foo/` or its subdirectories.

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/AppData/Roaming/foo/` with the same content.

#### 1.1.2. Linux

**Scenario**: Sync files under directory to default destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/.config/foo/` with the same content.

## 1.2. Destination specified

### 1.2.1. Windows

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { Windows: "bar/" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/bar/` with the same content.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { Windows: "" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: No-op

### 1.2.2. Linux

**Scenario**: Sync files under directory to specified destination

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { Linux: "bar/" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: Every file under `foo/` and its subdirectories has its counterpart file under `~/.config/bar/` with the same content.

**Scenario**: Skip sync

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": { dest: { Linux: "" }, policy: "copy" } }
```

where `foo/` is a directory in the repository root.

_Operation_: Run `recnys`
_Expectation_: No-op
