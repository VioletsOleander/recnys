# Recnys

Recnys is a simple tool for dotfile synchronization. I coded it primarily for personal use.

It supports Windows and Linux platforms.

## Installation

Use [uv](https://github.com/astral-sh/uv) for installation:

```shell
uv tool install recnys
```

After installation, there will be an executable named `recnys`.

## Usage

See the [specification document](./docs/specification.md) for the configuration file format. See the
[features document](./docs/features/) for the supported features.

With the configuration file correctly set, run `recnys` in the dotfile repository root, then the
synchronization will start:

```shell
recnys
```

> Tip: Consider adding an alias for `recnys`, since this name is not very intuitive. I personally
> alias it to `re` :).

Recnys supports dry-run mode. In this mode, no actual file operations will be performed, but the
actions that would be executed will be printed to the console.

If an error occurs during dry run, normally a helpful message will be printed to the console to
give you a hint about how to fix this error.

Therefore, it is highly recommended to first run `recnys` in dry-run mode to check if it will
perform the desired actions, and fix any possible errors in advance.

```shell
recnys --dry-run
```

If an error occurs during the actual run, don't worry, `recnys` is robust to interruption by storing
execution status under the `.recnys/` directory. All we need to do is following the printed hint to
fix this error and then rerun `recnys` to continue the execution from the last failure point.
