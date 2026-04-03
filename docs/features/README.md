# Features

## Introduction

The documents under this directory describe the features of Recnys. Each feature is described in a separate markdown file. The markdown files are organized in subdirectories according to use cases.

The following terms are reserved as keywords in the feature documents:

- "Requirement": Prerequisites for the feature to work. To use the feature, the user must ensure that the prerequisites
  are met.
- "Scenario": A specific use case that demonstrates how the feature works.
- "Condition": The state or situation corresponding to the scenario before the operation is performed.
- "Or": An alternative condition, used when there are multiple conditions corresponding to a scenario, and the operation and expectation described in the scenario is applicable to any of the conditions, without ambiguity.
- "Operation": The action performed by the user.
- "Expectation": The expected state or result after the operation is performed.
- "Scenario Background": One or more conditions shared by multiple scenarios under the same section.
- "Comment": Arbitrary text that provides additional information about the scenario, only used for explanation or clarification, and does not affect the scenario.
- "Pattern Definition": The definition of patterns used in the feature documents. Patterns are enclosed in double angle brackets, e.g., `<<pattern>>`, and are defined using regular expressions.
- "Variable Definition": The definition of variables used in the feature documents. Variables are enclosed in angle brackets, e.g., `<variable>`.
- "Glossary": The definition of terms used in the feature documents.

The "Requirement", "Variable Definition", "Pattern Definition" and "Glossary" defined in the `README.md` file under each subdirectory apply to all documents under the subdirectory and its subdirectories.

## Requirement

`recnys.yaml` exists in repository root.

## Pattern Definition

Define `<<any>>` as:

```regex
any = .*
```

Define `<<file>>` as:

```regex
file = ([^/]+/)*[^/]+
```

For example, `foo`, `foo/bar` and `foo/bar/baz` are all valid `<<file>>`, but `foo/` and `/foo` are not valid `<<file>>`.

Define `<<directory>>` as:

```regex
directory = ([^/]+/)+
```

For example, `foo/`, `foo/bar/` and `foo/bar/baz/` are all valid `<<directory>>`, but `foo` and `/foo/` are not valid `<<directory>>`.

## Variable Definition

Define `<os>` as:

```python
match platform.system():
    case "Windows": os = "Windows"
    case "Linux": os = "Linux"
```

Define `<home>` as:

```python
home = pathlib.Path.home()
```

Define `<config_directory>` as:

```python
match platform.system():
    case "Windows": config_directory = "AppData/Roaming/"
    case "Linux": config_directory = ".config/"
```

## Glossary

_File_:

- Static file: A file without `.template` suffix.
- Dynamic file: A file with `.template` suffix, also called template file. Dynamic files may contain [Jinja2 variables syntax](https://jinja.palletsprojects.com/en/stable/templates/#variables), and will be rendered using the provided variables before syncing to the destination.

_Counterpart path_:

- For directory: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the directory to the source directory.
- For static file: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the static file to the source directory.
- For dynamic file: a path under the destination directory whose relative path to the destination directory is the same as the relative path of the dynamic file to the source directory, but without `.template` suffix.

_Counterpart directory_: A directory in the counterpart path, containing:

- counterpart files and/or symlinks for files under the directory
- counterpart directories and/or symlinks for subdirectories under the directory

_Counterpart file_:

- For static file: a file in the counterpart path with the same content.
- For dynamic file: a file in the counterpart path with content rendered from the dynamic file.

_Counterpart symlink_:

- For directory: a symlink in the counterpart path pointing to the directory.
- For static file: a symlink in the counterpart path pointing to the static file.

_Artifact_:

- For static file: the resulting counterpart file or symlink of last `recnys` execution.
- For dynamic file: the resulting counterpart file of last `recnys` execution.
- For directory: the resulting counterpart directory or symlink of last `recnys` execution.
