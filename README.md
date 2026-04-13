# Recnys

Recnys is a simple tool for dotfiles synchronization. I coded it primarily for personal use.

It supports Windows and Linux platforms.

## Installation

Use [uv](https://github.com/astral-sh/uv) for installation:

```shell
uv tool install git+https://github.com/VioletsOleander/recnys
```

After installation, there will be a executable named `recnys`.

## Usage

Recnys requires a `recnys.yaml` configuration file defined in the root of the dotfile repository.
This configuration file gives instructions on which files to sync, where to sync, and how to sync.

Recnys supports using variables to render template files. This requires a `variables.yaml` file in the root of the dotfiles repository. Files that are to be rendered using these variables must have a `.template` suffix.

See the [specification document](./docs/specification.md) for more details about the syntax of the configuration file and the variables file.

With configuration file correctly set, run `recnys` in the dotfile repository root, the
synchronization will start:

```shell
recnys
```

> Tip: It is recommended to add an alias for `recnys`, since this name is not very intuitive. I personally alias it to `re` :).

Recnys supports dry-run mode. In this mode, no actual file operations will be performed, but the actions that would be taken are printed to the console. If there would be any issues about the synchronization, they will be printed to the console as well.

Therefore, it is highly recommended to first run `recnys` in a dry-run mode first to check if it will perform the desired actions.

```shell
recnys --dry-run
```
