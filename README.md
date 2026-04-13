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

Recnys requires a `recnys.yaml` configuration file defined in the root of the dotfile repository.
This configuration file gives instructions on which files to sync, where to sync, and how to sync.

An example `recnys.yaml` configuration file:

```yaml
{
  ".vimrc": { dest: { Windows: "_vimrc", Linux: ".vimrc" } },
  ".bashrc.template": { dest: { Windows: "", Linux: "my_bashrc" } },
  ".inputrc": { dest: { Windows: "", Linux: ".inputrc" } },
  ".tmux.conf": { dest: { Windows: "", Linux: ".tmux.conf" } },
  ".gitconfig": { dest: { Windows: ".gitconfig", Linux: ".gitconfig" } },
  "nvim/": { dest: { Windows: "AppData/Local/nvim" } },
  "yazi/",
  "lazygit/",
  "Microsoft/Windows Terminal/":
    {
      dest: { Linux: "", Windows: "AppData/Local/Microsoft/Windows Terminal/" },
    },
  "Code/User/settings.json",
  "Code/User/keybindings.json",
  "alacritty/",
  "vivid/",
  "nushell/",
  "nushell/autoload/net.nu.template",
}
```

The keys in the configuration file are the paths of the files or directories to be synchronized, relative to the root of the dotfile repository. The value of each key is an object that contains a `dest` field, which specifies the destination path for each platform.

As shown above, the destination of a file or directory can be specified for different platforms. If the destination for a platform is an empty string, then the file or directory will not be synchronized on that platform.

Notice that the paths in the destination field should be specified as relative to the user's home directory. For example, if the destination is `AppData/Local/nvim`, then the actual destination path will be `C:/Users/Username/AppData/Local/nvim` on Windows.

For normal file or directory, the default synchronization policy is to create a symbolic link at the destination pointing to the source file in the dotfile repository. For template files (files with `.template` suffix), the default synchronization policy is to render the template file using variables defined in `variables.yaml`, then write the rendered content to the destination.

It is support to use `policy` field to specify the synchronization policy for each file or directory. The value of the `policy` field can be either `symlink` or `copy`. If the `policy` field is not specified, then the default synchronization policy will be used.

For example, we can specify the synchronization policy for the `nushell/` directory to be `copy`:

```yaml
{ "nushell/": { dest: { Windows: "AppData/Local/nushell" }, policy: "copy" } }
```

Recnys supports using variables to render template files. This requires a `variables.yaml` file in the root of the dotfile repository. Files that are to be rendered using these variables must have a `.template` suffix.

Recnys uses "Last Win" strategy for deconflicting configuration entries. For example, when these two entries exist in the configuration file:

```yaml
{
  "nushell/", # sync the nushell directory
  "nushell/autoload/net.nu.template", # sync the net.nu.template file in the nushell directory
}
```

Recnys will make symbolic links for subdirectories and files in the `nushell/` directory, except for the `nushell/autoload/net.nu.template` file. Because this file is specified in latter entry, Recnys will render the `net.nu.template` file and write the rendered content to the destination.

For more information, please see the [specification document](./docs/specification.md) and the also the features document under `/docs/features/` directory.

With the configuration file correctly set, run `recnys` in the dotfile repository root, then the
synchronization will start:

```shell
recnys
```

> Tip: Consider adding an alias for `recnys`, since this name is not very intuitive. I personally alias it to `re` :).

Recnys supports dry-run mode. In this mode, no actual file operations will be performed, but the actions that would be execute will be printed to the console. If there would be any issues about the synchronization, they will be printed to the console as well.

Therefore, it is highly recommended to first run `recnys` in a dry-run mode to check if it will perform the desired actions.

```shell
recnys --dry-run
```
