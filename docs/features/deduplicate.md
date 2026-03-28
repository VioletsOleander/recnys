# Deduplicate

**Pattern Definition**:

Define `<<entry>>` as:

```regex
entry = foo | foo\.template | foo/ | foo/bar | foo/bar\.template
```

**Scenario**: Deduplicate between same entries

_Condition_: The content of `recnys.yaml` is:

```yaml
{
    "<<entry>>": <<any>>,
    "<<entry>>": <<any>>,
}
```

_Operation_: Run `recnys`

_Expectation_: Operation is performed for the last entry, the first entry is ignored.

## 1. File and File

**Scenario**: Deduplicate between static and dynamic file entries

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo": <<any>>, "foo.template": <<any>> }
```

_Or_ The content of `recnys.yaml` is:

```yaml
{ "foo.template": <<any>>, "foo": <<any>> }
```

_Or_ The content of `recnys.yaml` is:

```yaml
{ "foo/bar": <<any>>, "foo/bar.template": <<any>> }
```

and directory `foo/` contains file `bar` and `bar.template`.

_Or_ The content of `recnys.yaml` is:

```yaml
{ "foo/bar.template": <<any>>, "foo/bar": <<any>> }
```

and directory `foo/` contains file `bar` and `bar.template`.

_Operation_: Run `recnys`

_Expectation_: Operation is performed for the last entry, the first entry is ignored.

## 2. Directory and File

### 2.1. File and containing directory

**Scenario**: Containing directory entry wins

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar": <<any>>, "foo/": <<any>> }
```

and directory `foo/` contains file `bar`.

_Or_ The content of `recnys.yaml` is:

```yaml
{ "foo/bar.template": <<any>>, "foo/": <<any>> }
```

and directory `foo/` contains file `bar.template`.

_Operation_: Run `recnys`

_Expectation_: Operation is performed for `foo/`, the first entry is ignored.

### 2.2. Directory and contained file

**Scenario**: Contained file wins

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>>, "foo/bar": <<any>> }
```

and directory `foo/` contains file `bar`.

_Or_ The content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>>, "foo/bar.template": <<any>> }
```

and directory `foo/` contains file `bar.template`.

_Operation_: Run `recnys`

_Expectation_: Operation is performed for both entries, the artifact of the contained file corresponds to the file entry instead of the directory entry.

## 3. Directory and Directory

### 3.1. Subdirectory and containing directory

**Scenario**: Containing directory entry wins

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/bar/": <<any>>, "foo/": <<any>> }
```

and directory `foo/` contains subdirectory `bar/`.

_Operation_: Run `recnys`

_Expectation_: Operation is performed for `foo/`, the first entry is ignored.

### 3.2. Directory and contained subdirectory

**Scenario**: Contained subdirectory wins

_Condition_: The content of `recnys.yaml` is:

```yaml
{ "foo/": <<any>>, "foo/bar/": <<any>> }
```

and directory `foo/` contains subdirectory `bar/`.

_Operation_: Run `recnys`

_Expectation_: Operation is performed for both entries, the artifact of the contained subdirectory corresponds to the subdirectory entry instead of the directory entry.
