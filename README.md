# Recnys

Recnys is a simple tool for dotfile synchronization. I coded it primarily for personal use.

It supports Windows and Linux platforms.

## Installation

Use [uv](https://github.com/astral-sh/uv) for installation:

```shell
uv tool install git+https://github.com/VioletsOleander/recnys
```

After installation, there will be an executable named `recnys`.

## Usage

See the [specification document](./docs/specification.md) for the configuration file format. See the [features document](./docs/features/) for the supported features.

With the configuration file correctly set, run `recnys` in the dotfile repository root, then the
synchronization will start:

```shell
recnys
```

> Tip: Consider adding an alias for `recnys`, since this name is not very intuitive. I personally alias it to `re` :).

Recnys supports dry-run mode. In this mode, no actual file operations will be performed, but the actions that would be executed will be printed to the console. If there are any issues with synchronization, they will be printed to the console as well.

Therefore, it is highly recommended to first run `recnys` in dry-run mode to check if it will perform the desired actions.

```shell
recnys --dry-run
```
