# Recnys

Recnys is a simple dotfiles synchronization helper. I coded it primarily for personal use.

It supports Windows and Linux platforms.

It is called as "Recnys" because it is the reverse of "Syncer".

## Installation

Use [uv](https://github.com/astral-sh/uv) or [pipx](https://github.com/pypa/pipx) for installation:

```shell
uv tool install recnys
```

or

```shell
pipx install recnys
```

After installation, there will be two executables named `recnys` and `syncer`, with the same functionality.

## Usage

Recnys requires a `recnys.yaml` configuration file defined in the root of the dotfile repository.
This configuration file gives instructions on which files to sync, where to sync, and how to sync.

See `recnys.example.yaml` for detailed introduction about the configuration syntax.

With configuration file correctly set, run `recnys` or `syncer` in the dotfile repository root, the
synchronization will start. For example:

```shell
syncer
```

Recnys will prompt for confirmation request for each file's synchronization, specify `-f` or `--force` to
disable the behavior. For example:

```shell
syncer -f
```
