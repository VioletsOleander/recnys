# Recnys

Recnys is a simple dotfiles synchronization helper, mainly for personal use.

It supports Windows and Linux platform.

It is called as "Recnys" because it is the reverse of "Syncer".

## Installation

```shell
uv tool install recnys
```

After installation, there will be two executable named `recnys` and `syncer`, with the same functionality.

## Usage

Recnys requires there is a `recnys.yaml` configuration file defined in the root of the dotfile repository.
This configuration file gives instruction on which files to sync, where to sync, and how to sync.

See `recnys.example.yaml` for detailed introduction about the configuration syntax.

With configuration file correctly set, run `recnys` or `syncer` in the dotfile repository root, the
synchronization will start.

Recnys will pop out confirmation request for each files' synchronization, specify `-f` or `--force` to
disable the behavior.
