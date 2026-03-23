# Features

## Introduction

The documents under this directory describes the features of Recnys. Each feature is described in a separate markdown file. The markdown files are organized in subdirectories according to use cases.

The following terms are reserved as keywords in the feature documents:

- "Requirement": Prerequisites for the feature to work. To use the feature, the user must ensure that the prerequisites
  are met.
- "Scenario": A specific use case that demonstrates how the feature works.
- "Condition": The state or situation corresponding to the scenario before the operation is performed.
- "Operation": The action performed by the user.
- "Expectation": The expected state or result after the operation is performed.
- "Variable Definition": The definition of variables used in the feature documents. Variables are enclosed in angle brackets, e.g., `<variable>`.
- "Glossary": The definition of terms used in the feature documents.

The "Requirement", "Variable Definition" and "Glossary" defined in the `README.md` file under each subdirectory applies to all documents under the subdirectory and its subdirectories.

## Requirement

`recnys.yaml` exists in repository root.

## Variable Definition

Define `<os>` as:

```python
match platform.system():
    "Windows": os = "Windows"
    "Linux": os = "Linux"
```

## Glossary

_File_:

- Static file: A file without `.template` suffix.
- Dynamic file: A file with `.template` suffix, also called template file.
