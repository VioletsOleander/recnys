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

## Glossary

_Counterpart file_:

- For static file, its counterpart file is a file with the same name and same content.
- For dynamic file, its counterpart file is a file with the same name but without `.template` suffix and has the same content as the rendering result of the dynamic file.
