# 🔄 `logic/transformers` — Path In, Path Out

The `transformers` package holds the functions that turn one path into another: 
normalizing it, changing its suffix, moving it between two root directories, 
expressing it relative to a root, or finding a free name for it. 
`normalize_entry_path` provides a different kind of normalization for operations 
on directory entries: it resolves the containing directory while keeping 
the final name untouched. None of these functions changes the disk — `make_unique_path` 
only *looks* at it — which is why they live apart from the functions in [`ensure`](README_PATH_ENSURE.md) that do.

```python
from simplibs.path import normalize_path, rebase_path, change_suffix
```

Every function accepts its path as a [`PathLike`](../README_PATH_ANNOTATIONS.md#pathlike) — a
non-blank `str` or a `Path` — and is wrapped in `@validate_call`, so a blank string or a
wrong type is rejected with a `ValidationError` before the body runs.

## A note on what "normalized" means

Two normalization strategies serve different purposes:

- `normalize_path` identifies the location of the content: it expands `~`, 
  collapses relative components, makes the path absolute and, by default, 
  resolves symlinks all the way to their targets.
- `normalize_entry_path` identifies a directory entry itself: it resolves 
  the containing directory but preserves the final name as written, without 
  following a symlink in that position.

This distinction matters when an operation acts on a name rather than its target. 
For example, deleting a symlink should remove the link itself, not the file it points to. 
`make_unique_path` therefore uses `normalize_entry_path`, while operations that need 
the resolved content location can use `normalize_path`.

`change_suffix` is deliberately *lexical*: it changes the path's text without 
accessing the filesystem or expanding the home directory.

---

## 🧭 Table of Contents

* [`normalize_path`](#normalize_path)
* [`normalize_entry_path`](#normalize_entry_path)
* [`rebase_path`](#rebase_path)
* [`relativize_path`](#relativize_path)
* [`change_suffix`](#change_suffix)
* [`make_unique_path`](#make_unique_path)

[⬅️ Back to main README](../../README.md#-logictransformers--path-in-path-out)

---

### `normalize_path`

Normalizes a path into an absolute, `~`-expanded `Path` with relative components
collapsed and, by default, symlinks resolved. The path does **not** have to exist.

**Parameters:**

* `path` (*PathLike*): The path to normalize.
* `resolve_symlinks` (*bool*, keyword-only, default `True`): If `True`, symlinks are
  followed and the real location is returned. If `False`, the path is only made
  absolute and `.`/`..` are collapsed lexically — symlinks stay as written.

**Returns:**

* `Path`: An absolute path.

**Raises:**

* `AccessError`: The path cannot be resolved — an OS-level error, a symlink loop, or
  invalid text such as an embedded null byte.

**Example usage:**

```python
normalize_path("~/project/../project/src")
# -> PosixPath('/home/me/project/src')

# Keep a symlinked location as written (data -> /mnt/storage stays "data"):
normalize_path("data/file.txt", resolve_symlinks=False)
```

**Under the hood:**

```python
@validate_call
def normalize_path(path: PathLike, *, resolve_symlinks: bool = True) -> Path:
    # A null byte is invalid in every path — same error in both modes
    if "\0" in str(path):
        raise_normalize_path_error(path, ValueError("embedded null byte"))

    try:
        expanded = Path(path).expanduser()
        if resolve_symlinks:
            return expanded.resolve()
        return Path(os.path.abspath(expanded))          # lexical, symlinks untouched
    except (OSError, RuntimeError, ValueError) as caught_exc:
        raise_normalize_path_error(path, caught_exc)
```

`RuntimeError` is caught because a symlink loop surfaces as one before Python 3.13 (and
as `OSError` afterwards); catching all three keeps the error card stable across versions.

[▲ Back to top](#-table-of-contents)

---

---

### `normalize_entry_path`

Normalizes the path of a directory entry rather than resolving the content behind it. 
The containing directory is resolved, but the final name remains untouched. 
This distinction is important for operations such as deleting, renaming, 
moving or checking the availability of a name: a symlink in the final position 
must remain a symlink, not be replaced by its target.

**Parameters:**

- `path` (*PathLike*): The path of the directory entry.

**Returns:**

- `Path`: An absolute path with `~` expanded and relative components collapsed. 
  Symlinks in the directory portion are resolved, but the final name is preserved 
  exactly as written. The entry itself does not have to exist.

**Raises:**

- `ParamError`: `path` has no final name, as with a filesystem root.
- `AccessError`: The directory portion cannot be resolved.

**Example usage:**

```python
# Resolve the containing directory, keeping the final name unchanged:
normalize_entry_path("data/link.txt")
# -> /resolved/data/link.txt

# The final symlink is not followed:
# If "data/link.txt" points to "/other/target.txt",
# the result still ends in "link.txt", not "target.txt".

# A filesystem root has no entry name:
normalize_entry_path("/")
# -> raises ParamError
```

**Under the hood:**

```python
lexical = normalize_path(path, resolve_symlinks=False)

if not lexical.name:
    raise_path_has_no_name_error(lexical)

return normalize_path(lexical.parent) / lexical.name
```

The first normalization makes the path absolute without following a symlink in 
its final name. The function then resolves only the parent directory and joins 
it with the preserved final name. This also canonicalizes paths that reach 
the same directory through different symlinked directory paths.

Use `normalize_path` when you need the resolved location of the content. 
Use `normalize_entry_path` when you need the canonical directory entry 
to operate on the name itself.

[▲ Back to top](#-table-of-contents)

---

### `rebase_path`

Maps a path inside one root directory to the same place inside another —
`src/pkg/a.py` with `source_root="src"` and `target_root="out"` becomes `out/pkg/a.py`.
The "where does the output of this input go" step of a processing pipeline. It is pure
path arithmetic: **nothing is created** (pair it with
[`ensure_parent_dir`](README_PATH_ENSURE.md#ensure_parent_dir) before writing).

**Parameters:**

* `path` (*PathLike*): The path inside `source_root`.
* `source_root` (*PathLike*, keyword-only): The directory `path` currently lives in.
* `target_root` (*PathLike*, keyword-only): The directory the result should live in.
* `new_suffix` (*str | None*, keyword-only, default `None`): If given, the result's
  suffix is replaced as by [`change_suffix`](#change_suffix). `None` keeps the name;
  `""` removes the suffix — two different requests, which is why the default is `None`.

**Returns:**

* `Path`: The rebased, normalized path.

**Raises:**

* `ParamError`: `path` is not located inside `source_root`, or `new_suffix` is malformed.
* `AccessError`: A path cannot be normalized.

**Example usage:**

```python
rebase_path("src/pkg/a.py", source_root="src", target_root="out")
# -> <cwd>/out/pkg/a.py

rebase_path("src/pkg/a.py", source_root="src", target_root="out", new_suffix=".md")
# -> <cwd>/out/pkg/a.md
```

**Under the hood:**

```python
normalized_path   = normalize_path(path)
normalized_source = normalize_path(source_root)
normalized_target = normalize_path(target_root)

try:
    relative = normalized_path.relative_to(normalized_source)
except ValueError:
    raise_path_not_within_root_error(normalized_path, normalized_source)

rebased = normalized_target / relative
return change_suffix(rebased, new_suffix) if new_suffix is not None else rebased
```

All three paths are normalized the same way first — otherwise `./src` and `/abs/src`, or a
symlinked and a resolved root, would wrongly fail to match.

[▲ Back to top](#-table-of-contents)

---

### `relativize_path`

Expresses a path relative to a root directory — shows a collected path the way it
appears inside the scanned tree (`src/a/b.py` instead of an absolute path).

**Parameters:**

* `path` (*PathLike*): The path to relativize.
* `root` (*PathLike*, keyword-only): The directory the result is relative to.

**Returns:**

* `Path`: The path relative to `root` — `Path(".")` when both are the same.

**Raises:**

* `ParamError`: `path` is not located inside `root`.
* `AccessError`: A path cannot be normalized.

**Example usage:**

```python
relativize_path("/home/me/project/src/a.py", root="/home/me/project")
# -> PosixPath('src/a.py')

relativize_path("/home/me/project", root="/home/me/project")
# -> PosixPath('.')
```

**Under the hood:**

```python
normalized_path = normalize_path(path)
normalized_root = normalize_path(root)
try:
    return normalized_path.relative_to(normalized_root)
except ValueError:
    raise_path_not_within_root_error(normalized_path, normalized_root)
```

Comparison is by whole path *parts*: `/data/src2` is not inside `/data/src`.

[▲ Back to top](#-table-of-contents)

---

### `change_suffix`

Replaces, adds or removes the last suffix of a path. **Lexical:** it never touches the
disk and does not expand `~` — combine with
[`normalize_path`](#normalize_path) when you need that.

**Parameters:**

* `path` (*PathLike*): The path whose suffix changes.
* `new_suffix` (*str*): The new suffix including the dot (`".md"`), or `""` to remove the
  current one. A valid suffix is empty or a dot plus at least one character, with no
  `/`, `\` or null byte.

**Returns:**

* `Path`: A new path. Only the **last** suffix is replaced: `archive.tar.gz` + `".zip"`
  becomes `archive.tar.zip`.

**Raises:**

* `ParamError`: `new_suffix` is malformed, or `path` has no final name (a filesystem
  root, `.` or `..`).

**Example usage:**

```python
change_suffix("dir/report.txt", ".md")    # -> dir/report.md
change_suffix("dir/report", ".md")        # -> dir/report.md     (added)
change_suffix("dir/report.txt", "")       # -> dir/report        (removed)
change_suffix("a.txt", "md")              # -> raises ParamError (missing dot)
```

**Under the hood:**

```python
@validate_call
def change_suffix(path: PathLike, new_suffix: str) -> Path:
    if not is_valid_suffix(new_suffix):
        raise_invalid_suffix_error(new_suffix)

    result = Path(path)
    if result.name in ("", ".."):
        raise_path_has_no_name_error(result)

    return result.with_suffix(new_suffix)
```

The suffix is validated up front because `Path.with_suffix` has terse, version-dependent
errors and lets `..` through (producing the name `...md`). The shape check
(`is_valid_suffix`) is shared with the [`HasSuffix`](../README_PATH_RULES.md#hassuffix) rule.

[▲ Back to top](#-table-of-contents)

---

### `make_unique_path`

Returns the path itself if nothing occupies it, otherwise the first free numbered variant
— `report.txt` → `report (1).txt` → `report (2).txt` — the way file managers name copies.
Nothing is created.

**Parameters:**

* `path` (*PathLike*): The wanted path.
* `max_attempts` (*int*, keyword-only, default `1000`): How many numbered variants to try
  before giving up. Must be positive.

**Returns:**

* `Path`: An absolute path that did not exist at the moment of the call. Its *directory*
  is resolved (symlinks followed); the *final name* is kept as written, so a symlink there
  is never followed.

**Raises:**

* `ParamError`: `path` has no final name (a filesystem root).
* `OperationError`: Every variant up to `max_attempts` is taken.
* `AccessError`: The path cannot be normalized.

**Example usage:**

```python
make_unique_path("out/report.txt")        # -> out/report.txt          (free)
make_unique_path("out/report.txt")        # -> out/report (1).txt      (report.txt exists)
make_unique_path("out/archive.tar.gz")    # -> out/archive (1).tar.gz  (.tar.gz stays together)
make_unique_path(".env")                  # -> .env (1)                (a dotfile has no suffix)
```

**Under the hood:**

```python
# Normalize the wanted path as a directory entry:
# resolve the directory, preserve the final name.
normalized = normalize_entry_path(path)

if not os.path.lexists(normalized):
    return normalized

stem, suffix = split_name(normalized)  # ".tar.gz"-aware
for number in range(1, max_attempts + 1):
    candidate = normalized.with_name(f"{stem} ({number}){suffix}")
    if not os.path.lexists(candidate):
        return candidate

raise_unique_path_exhausted_error(normalized, max_attempts)
```

`normalize_entry_path` centralizes the distinction between the directory and the final name. 
`os.path.lexists` ensures that even a broken symlink occupies its name, while `split_name` 
preserves compound suffixes such as `.tar.gz`.

> **Not a reservation.** The name is free *when the function returns*. To claim it for
> certain, open the result with mode `"x"` (exclusive creation); this function only
> chooses a good candidate.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logictransformers--path-in-path-out)
