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

- a normal file, e.g. `".vimrc"`
- a template file (ending with `.template`), e.g. `".bashrc.template"`
- a directory (ending with `/`), e.g. `"nvim/"`

`<src>` should be surrounded by double quotes (`"`), and should be a path relative to the dotfiles repository root, i.e. the parent directory of `recnys.yaml`.

The template files will be rendered using the provided variables, and its rendered result will be synced to the destination.

#### `dest`

`dest` describes the destination path on different platforms.

`dest` is optional. For a certain platform, if the destination path is not provided, it will be derived from the source path:

- In Linux, it defaults to `~/.config/src` (without `.template` suffix if `<src>` is a template file).
- In Windows it defaults to `~/AppData/Roaming/src` (without `.template` suffix if `<src>` is a template file).

> Tip: `~/` means the user's home directory

Destination path should be surrounded by double quotes (`"`), and should be a relative path to the user's home directory.

For a certain platform, if the destination path is an empty string (`""`), it means the entry is disabled on the platform, and no operation will be performed for the entry on the platform.

#### `policy`

`policy` describes how to sync the source file/directory to the destination, which can be:

- `copy` means copy the file/directory from the source to the destination, and overwrite the destination if it already exists.
- `symlink` means create a symlink at the destination pointing to the source, and overwrite the destination if it already exists.
- `render` means render the source file (only applicable for template files) and copy the rendered result to the destination, and overwrite the destination if it already exists.

`policy` is optional. It defaults to `symlink` for normal file and directory, and defaults to `render` for template file.

Template files do not support `copy` policy (`render` policy already does copy) and `symlink` policy (to maintain a single source of truth).

### 1.2. Conflict Resolution

In a word, the latter wins.

Refer to [the corresponding feature](features/deconflict.md) for details.

## 2. `variables.yaml`

This file should be placed in the root of the dotfiles repository.

This file consists of a dictionary, each key-value pair in it describing a variable for template rendering. The key is the variable name, and the corresponding value is the variable value.

These variables will be for rendering the template files (ending with `.template`) in `recnys.yaml`.

```yaml
{ proxy_url: "http://proxy.example.com:8080" }
```
