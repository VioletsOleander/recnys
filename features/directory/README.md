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

_Counterpart path_:

- For sub-directory: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the sub-directory to the source directory.
- For static file: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the static file to the source directory.
- For dynamic file: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the dynamic file to the source directory, but without `.template` suffix.

_Counterpart file_:

- For static file: a file in the counterpart path with the same content.
- For dynamic file: a file in the counterpart path with content rendered from the dynamic file.

_Counterpart symlink_:

- For sub-directory: a symlink in the counterpart path pointing to the sub-directory.
- For static file: a symlink in the counterpart path pointing to the static file.
