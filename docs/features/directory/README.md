# Directory

## Requirement

`foo/` exists in the repository root.

## Variable Definition

Define `<default_directory>` as:

```python
match platform.system():
    case "Windows": default_directory = "~/AppData/Roaming/foo/"
    case "Linux": default_directory = "~/.config/foo/"
```
