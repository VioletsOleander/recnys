# Configuration file specification

## 1. `recnys.yaml`

This file should be placed in the root of the dotfiles repository.

### 1.1 Basic Syntax

This file consists of a dictionary, each key-value pair in the dictionary is called an entry, and each entry describes the syncing configuration for a source file/directory in the dotfiles repository.

The syntax of a single entry dictionary is as follows:

```yaml
{
  <src>:
    {
      dest: { Linux: <dest_linux>, Windows: <dest_windows> },
      policy: <policy>,
    },
}
```

where `<src>` is required, `dest` and `policy` are optional.

> Note: 'Linux' and 'Windows' are case sensitive, and should be capitalized as shown here

#### `<src>`

`<src>` describes the source path of the file/directory to sync in the dotfiles repository, which can be:

- a static file, e.g. `".vimrc"`
- a dynamic file (ending with `.template`), e.g. `".bashrc.template"`
- a directory (ending with `/`), e.g. `"nvim/"`

`<src>` should be surrounded by double quotes (`"`), and should be a path relative to the dotfiles repository root, i.e. the parent directory of `recnys.yaml`.

The dynamic files will be rendered using the provided variables, and its rendered result will be synced to the destination.

See [glossaries](features/README.md#glossary) for the definition of static and dynamic files.

#### `dest`

`dest` describes the destination path on different platforms.

`dest` is optional. For a certain platform, if the destination path is not provided, it will be derived from the source path with a default rule:

- If `<src>` is a file under repository root (e.g. `.vimrc`), the `dest` in Linux/Windows defaults to `~/src` (without `.template` suffix if `<src>` is a dynamic file).
- If `<src>` is a directory (e.g. `nvim/`), the `dest` in Linux default to `~/.config/src`, and in Windows defaults to `~/AppData/Roaming/src`.
- If `<src>` is a file under a specified directory (e.g. `nushell/config.nu`), the `dest` in Linux defaults to `~/.config/src`, and in Windows defaults to `~/AppData/Roaming/src` (without `.template` suffix if `<src>` is a dynamic file).

> Tip: `~/` means the user's home directory

Destination path should be surrounded by double quotes (`"`), and should be a path relative to the user's home directory.

For a certain platform, if the destination path is an empty string (`""`), it means the entry is disabled on the platform, and no operation will be performed for the entry on the platform.

For example, the following entry:

```yaml
{ ".vimrc": { dest: { Windows: "_vimrc" } } }
```

describes that:

- the source file is `.vimrc` in the dotfiles repository.
- the destination path in Windows is `~/_vimrc`.
- the destination path in Linux is not provided, so defaults to `~/.vimrc`.

#### `policy`

`policy` describes how to sync the source file/directory to the destination, which can be:

- `copy` means copy the file/directory from the source to the destination, and overwrite the destination if it already exists.
- `symlink` means create a symlink at the destination pointing to the source, and overwrite the destination if it already exists.

`policy` is optional. It defaults to `symlink` for static file and directory, and defaults to `copy` for dynamic file.

**Notice**: In order to maintain a single source of truth, dynamic files do not support `symlink` policy:

- A file entry with dynamic file as source and `symlink` as policy is considered invalid.
- A directory entry containing dynamic files and with `symlink` as policy is considered as a special case. This directory will not be symlinked, but created as a regular directory in the destination path, and the subdirectories under it will be symlinked if they do not contain dynamic files, otherwise they will be created as regular directories, and the static files under it will be symlinked, but the dynamic files under it will be rendered and **copied** to the destination path. Refer to [the corresponding feature](features/directory/symlink.md#2-directory-contains-dynamic-files) for details.

### 1.2. Conflict Resolution

In a word, the latter wins.

Refer to [the corresponding feature](features/deduplicate.md) for details.

## 2. `variables.yaml`

This file should be placed in the root of the dotfiles repository.

This file consists of a dictionary, each key-value pair in it describing a variable for template rendering. The key is the variable name, and the corresponding value is the variable value.

These variables will be for rendering the dynamic files (ending with `.template`) in `recnys.yaml`.

```yaml
{ proxy_url: "http://proxy.example.com:8080" }
```
