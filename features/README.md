# Features

## Introduction

The documents under this directory describe the features of Recnys. Each feature is described in a separate markdown file. The markdown files are organized in subdirectories according to use cases.

The following terms are reserved as keywords in the feature documents:

- "Requirement": Prerequisites for the feature to work. To use the feature, the user must ensure that the prerequisites
  are met.
- "Scenario": A specific use case that demonstrates how the feature works.
- "Condition": The state or situation corresponding to the scenario before the operation is performed.
- "Operation": The action performed by the user.
- "Expectation": The expected state or result after the operation is performed.
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

## Variable Definition

Define `<os>` as:

```python
match platform.system():
    case "Windows": os = "Windows"
    case "Linux": os = "Linux"
```

## Glossary

_File_:

- Static file: A file without `.template` suffix.
- Dynamic file: A file with `.template` suffix, also called template file.

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
