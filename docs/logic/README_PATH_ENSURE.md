# 🏗️ `logic/ensure` — Make a State True

The `ensure` package holds the functions that **change the disk**: each makes one
filesystem state true — a directory exists, a file exists, a path's folder exists — and
returns the normalized path, so it chains straight into the next step. They are the only
functions in the library that write anything, which is why they live apart from the pure
[`transformers`](README_PATH_TRANSFORMERS.md).

```python
from simplibs.path import ensure_dir, ensure_file, ensure_parent_dir
```

Every function is **idempotent** — calling it again changes nothing — and **never touches
existing content**: an existing directory is returned as it is, an existing file is not
truncated and keeps its timestamp.

## A note on errors

Failures are reported as structured cards, never as a bare `OSError`:

| Situation                                                     | Exception     |
|---------------------------------------------------------------|---------------|
| A file is where a directory is needed (or the other way round) | `StateError`  |
| A required file is missing and `create=False`                  | `NotFoundError` |
| Permissions, a read-only disk, another OS-level refusal       | `AccessError` |

A race ("a file appeared between the check and the `mkdir`") is reported as the
`StateError` it really is — not as a misleading permissions error.

## A note on symlinks

Paths are [normalized](README_PATH_TRANSFORMERS.md#normalize_path) first, so symlinks are
followed. `ensure_dir("link")` for a *dangling* link creates the directory the link
**points to**. That is the same meaning of "this path" everywhere in the library.

---

## 🧭 Table of Contents

* [`ensure_dir`](#ensure_dir)
* [`ensure_file`](#ensure_file)
* [`ensure_parent_dir`](#ensure_parent_dir)

[⬅️ Back to main README](../../README.md#-logicensure--make-a-state-true)

---

### `ensure_dir`

Guarantees that a directory exists, creating it — and any missing parents — if necessary.

**Parameters:**

* `path` (*PathLike*): The directory path to guarantee.

**Returns:**

* `Path`: The normalized, guaranteed-to-exist directory.

**Raises:**

* `StateError`: Something that is not a directory (a file) already occupies the path.
* `AccessError`: The directory cannot be created.

**Example usage:**

```python
ensure_dir("out/reports/2026")      # creates out/, out/reports/ and out/reports/2026/
ensure_dir("out")                   # already there — returned as it is, nothing touched
ensure_dir("notes.txt")             # a file -> raises StateError
```

**Under the hood:**

```python
normalized_path = normalize_path(path)

if normalized_path.exists():
    if not normalized_path.is_dir():
        raise_ensure_dir_not_a_dir_error(normalized_path)
    return normalized_path

try:
    normalized_path.mkdir(parents=True, exist_ok=True)
except OSError as caught_exc:
    # something else took the name meanwhile — a state problem, not a permission problem
    if os.path.lexists(normalized_path) and not normalized_path.is_dir():
        raise_ensure_dir_not_a_dir_error(normalized_path)
    raise_ensure_dir_error(normalized_path, caught_exc)

return normalized_path
```

[▲ Back to top](#-table-of-contents)

---

### `ensure_file`

Guarantees that a path points to a file, optionally creating it — and its parent
directory — if missing.

**Parameters:**

* `path` (*PathLike*): The file path to guarantee.
* `create` (*bool*, keyword-only, default `True`): Create the file (and its folder) when
  missing. With `False`, a missing file raises instead — turning the function into a pure
  **precondition** that passes an existing file on or fails with `NotFoundError`.

**Returns:**

* `Path`: The normalized, guaranteed-to-exist file.

**Raises:**

* `StateError`: The path is a directory, or a file sits in the parent chain.
* `NotFoundError`: The file is missing and `create=False`.
* `AccessError`: The file cannot be created.

**Example usage:**

```python
ensure_file("logs/app.log")                  # creates logs/ and an empty app.log
ensure_file("logs/app.log")                  # exists — content untouched
ensure_file("config.toml", create=False)     # must already exist, else NotFoundError
ensure_file("a_file/new.txt")                # a_file is a file -> StateError naming it
```

**Under the hood:**

```python
normalized_path = normalize_path(path)

if normalized_path.exists():
    if not normalized_path.is_file():
        raise_ensure_file_not_a_file_error(normalized_path)
    return normalized_path

if not create:
    raise_ensure_file_not_found_error(normalized_path)

ensure_dir(normalized_path.parent)              # a file in the chain fails here, with its name
try:
    normalized_path.touch(exist_ok=True)
except OSError as caught_exc:
    if os.path.lexists(normalized_path) and not normalized_path.is_file():
        raise_ensure_file_not_a_file_error(normalized_path)
    raise_ensure_file_create_error(normalized_path, caught_exc)

return normalized_path
```

`touch` only runs for a path that did not exist, so an existing file is never truncated
and keeps its modification time.

[▲ Back to top](#-table-of-contents)

---

### `ensure_parent_dir`

Guarantees that the directory a path lives in exists — **without creating the path
itself**. The step right before writing an output file: the file is not there yet, but its
folder must be.

**Parameters:**

* `path` (*PathLike*): The path, usually of a file about to be written.

**Returns:**

* `Path`: The normalized path **itself** — not its parent — so the call chains straight
  into the write.

**Raises:**

* `StateError`: A file occupies the place of a needed directory.
* `AccessError`: The parent directory cannot be created.

**Example usage:**

```python
target = ensure_parent_dir("out/pkg/a.md")     # out/pkg/ now exists; a.md does not
target.write_text("# Result")                  # the writer creates the file itself
```

**Under the hood:**

```python
normalized_path = normalize_path(path)
ensure_dir(normalized_path.parent)
return normalized_path
```

Creating the *file* up front (`ensure_file`) is wrong when the writer wants to create it
itself — with its own content, mode or encoding. In a pipeline the value flowing on is the
file's path, which is why this returns it:
`RebasePath(...) >> EnsureParentDir() >> write_step`.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicensure--make-a-state-true)
