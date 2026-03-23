# Features

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
