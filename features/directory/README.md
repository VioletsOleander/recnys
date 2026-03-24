# Directory

## Requirement

`foo/` exists in the repository root.

## Variable Definition

Define `<default_directory>` as:

```python
match platform.system():
    "Windows": default_directory = "~/AppData/Roaming/foo/"
    "Linux": default_directory = "~/.config/foo/"
```
