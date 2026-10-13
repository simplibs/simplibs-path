# ✅ `logic/checks` — Predicates That Never Raise

The `checks` package holds the predicate functions that have real logic behind them. Each
returns a plain `bool`, and treats **anything the operating system refuses as `False`** —
a missing path, a permission problem, a bad name, a path behind a folder you may not
enter. Only a wrong *type* of argument is an error (a `ValidationError`, from the
`PathLike` annotation).

```python
from simplibs.path import is_within, is_path_writable, is_valid_filename
```

## A note on what is *not* here

Checks that are a single `pathlib` call — `exists`, `is_file`, `is_dir`, `is_symlink`,
`is_absolute` — have no function in this package, because a wrapper that only forwards
would add a name without adding anything. Their **rules**
([`PathExists`](../README_PATH_RULES.md#pathexists), [`IsFile`](../README_PATH_RULES.md#isfile), ...)
call `pathlib` directly and add the one thing the raw calls lack: they never raise
(`Path.is_file()` itself re-raises `PermissionError` for a path behind a locked folder).

## A note on `_validate_call`

Every function here also accepts a reserved keyword-only `_validate_call: bool = True`.
The rules in [`rules/`](../README_PATH_RULES.md) pass `False`, because they have already
checked the type of their input and run these functions once per entry over thousands of
paths. Ordinary callers can ignore it.

## A note on timing

Every answer holds **at the moment of the call**. Another process can change permissions,
fill the disk or create a file right after. Use these as fail-fast checks with good
messages, not as reservations — a real write must still handle its own errors.

---

## 🧭 Table of Contents

* [`is_path_readable`](#is_path_readable)
* [`is_path_writable`](#is_path_writable)
* [`is_empty_dir`](#is_empty_dir)
* [`is_hidden_path`](#is_hidden_path)
* [`is_within`](#is_within)
* [`is_valid_filename`](#is_valid_filename)

[⬅️ Back to main README](../../README.md#-logicchecks--predicates-that-never-raise)

---

### `is_path_readable`

Checks whether a file can be read, or a directory listed.

**Parameters:**

* `path` (*PathLike*): The file or directory to check.

**Returns:**

* `bool`: `True` for an existing regular file that can be opened for reading, or an
  existing directory whose entries can be listed. `False` for everything else — a missing
  path, a broken symlink, a FIFO, a device, or access denied.

**Example usage:**

```python
is_path_readable("notes.txt")        # -> True
is_path_readable("/root/secret")     # -> False   (no permission — no exception)
is_path_readable("missing.txt")      # -> False
```

**Under the hood:**

```python
candidate = to_path(path)
if candidate is None:
    return False
try:
    if candidate.is_dir():
        with os.scandir(candidate):
            return True
    if candidate.is_file():
        with candidate.open("rb"):
            return True
except (OSError, ValueError):
    return False
return False
```

The file is actually **opened** (and the directory actually listed) rather than asked
through `os.access`: on Windows `os.access` ignores ACLs, and nowhere can it see a file
locked by another process. Opening for reading changes nothing on disk. Special files
(FIFOs, sockets, devices) answer `False` without being touched, because opening them can
block.

[▲ Back to top](#-table-of-contents)

---

### `is_path_writable`

Checks whether a path could be written to *right now* — **without creating or changing
anything**.

**Parameters:**

* `path` (*PathLike*): An existing file, an existing directory, or a file that does not
  exist yet.

**Returns:**

* `bool`: `True` if an existing file can be opened for appending, if a file can be created
  inside an existing directory, or if a missing file's parent directory exists and accepts
  new files. `False` otherwise — including a **missing parent directory** (nothing is
  created here; that is [`ensure_parent_dir`](README_PATH_ENSURE.md#ensure_parent_dir)'s job).

**Example usage:**

```python
is_path_writable("out/report.txt")      # -> True   (out/ exists and accepts files)
is_path_writable("out")                 # -> True   (a directory that accepts files)
is_path_writable("missing/x.txt")       # -> False  (no such folder — and none is created)
```

**Under the hood:**

```python
candidate = to_path(path)
if candidate is None:
    return False
try:
    if candidate.is_dir():
        return can_create_inside(candidate)
    if candidate.is_file():
        with candidate.open("ab"):            # append mode never changes the content
            return True
    if os.path.lexists(candidate):            # a broken symlink or a device holds the name
        return False
    parent = candidate.parent
    return parent.is_dir() and can_create_inside(parent)
except (OSError, ValueError):
    return False
```

`can_create_inside` creates an anonymous temporary file in the directory and discards it
(it never appears under a name that survives, even if the process is killed). It is the
only check that matches what a later write experiences — `os.access(path, W_OK)` mostly
answers "yes" for a Windows directory and ignores read-only mounts.

> The earlier implementation opened *any* path in append mode, which **created an empty
> file** for a path that did not exist — a "check" with a lasting side effect.

[▲ Back to top](#-table-of-contents)

---

### `is_empty_dir`

Checks whether a path is an existing directory with no entries.

**Parameters:**

* `path` (*PathLike*): The path to check.

**Returns:**

* `bool`: `True` only for an existing, listable, empty directory. `False` for a non-empty
  directory, a file, a missing path — and for a directory that **cannot be listed**
  (its emptiness is unknown, and "not proven empty" is the safe side for a cleanup decision).

**Example usage:**

```python
is_empty_dir("build/output")      # -> True   (exists, nothing inside)
is_empty_dir("src")               # -> False  (has files)
is_empty_dir("notes.txt")         # -> False  (not a directory)
```

**Under the hood:**

```python
try:
    with os.scandir(candidate) as entries:
        return next(entries, None) is None      # first entry only
except (OSError, ValueError):
    return False
```

Only the first entry is read — a directory with a million files costs the same as an empty one.

[▲ Back to top](#-table-of-contents)

---

### `is_hidden_path`

Checks whether a path's final name marks it as hidden.

**Parameters:**

* `path` (*PathLike*): The path to check. Only its **final name** is considered, not the
  directories above it.
* `check_attributes` (*bool*, keyword-only, default `False`): On Windows, an existing path
  carrying the "hidden" file attribute also counts. Ignored elsewhere.

**Returns:**

* `bool`: `True` if the final name starts with a dot (`.git`, `.env`), or — with
  `check_attributes` on Windows — the hidden attribute is set. `.` and `..` are never hidden.

**Example usage:**

```python
is_hidden_path(".git")                          # -> True
is_hidden_path("project/.env")                  # -> True
is_hidden_path("/home/me/.config/tool/a.json")  # -> False  (only the final name counts)
is_hidden_path("report.txt", check_attributes=True)   # -> True if Windows marked it hidden
```

**Under the hood:**

```python
name = candidate.name
if name.startswith(".") and name not in (".", ".."):
    return True

if check_attributes and os.name == "nt":
    try:
        attributes = getattr(candidate.stat(), "st_file_attributes", 0)
    except OSError:
        return False
    return bool(attributes & stat.FILE_ATTRIBUTE_HIDDEN)
return False
```

The dot convention costs no disk access, which matters in a filter running over a whole
tree, and behaves the same on every platform. The Windows attribute needs a `stat` call
per path, so it is opt-in. Skipping whole hidden *folders* is what a scanner's
[`ignore_names`](README_PATH_SCANNERS.md#ignore_names--what-a-scan-skips) does.

[▲ Back to top](#-table-of-contents)

---

### `is_within`

Checks whether a path lies **inside** a root directory — the guard against path traversal
(`../../etc/passwd` must not leave the output folder).

**Parameters:**

* `path` (*PathLike*): The path to test.
* `root` (*PathLike*): The directory it is supposed to be inside.
* `resolve_symlinks` (*bool*, keyword-only, default `True`): Resolve symlinks and `..`
  before comparing, so a link pointing out of `root` does **not** count as inside. `False`
  makes the comparison purely lexical (cheaper; enough for paths a scanner already
  normalized).
* `allow_equal` (*bool*, keyword-only, default `True`): Whether a path equal to `root`
  itself counts as inside.

**Returns:**

* `bool`: `True` if `path` is inside `root` (or equal to it, when allowed). Unresolvable
  input is `False` — a security check that raises can be skipped by a broad `except`; one
  that answers `False` fails closed.

**Example usage:**

```python
is_within("out/reports/a.md", "out")              # -> True
is_within("out/../secret.txt", "out")             # -> False  (the .. escapes)
is_within("out2/a.md", "out")                     # -> False  ("out2" is not "out")
is_within("out", "out", allow_equal=False)        # -> False
```

**Under the hood:**

```python
if resolve_symlinks:
    candidate, base = candidate.resolve(), base.resolve()
else:
    candidate, base = Path(os.path.abspath(candidate)), Path(os.path.abspath(base))

if candidate == base:
    return allow_equal
return candidate.is_relative_to(base)
```

`str(path).startswith(str(root))` is wrong in three ways — `/data/src2` starts with
`/data/src`, `..` hides an escape, and Windows compares case-insensitively.
`Path.is_relative_to` on normalized absolute paths compares whole path *parts*, with the
platform's own case rules.

[▲ Back to top](#-table-of-contents)

---

### `is_valid_filename`

Checks whether a **string** is usable as a single file or directory name.

**Parameters:**

* `name` (*str*): The candidate — a *name*, not a path (`"dir/file.txt"` is not a valid name).
* `portable` (*bool*, keyword-only, default `True`): The name must be valid on both Windows
  and POSIX systems. `False` applies only the rules of the current operating system.

**Returns:**

* `bool`: `True` if the name has no problem; `False` otherwise.

The rules, applied in order:

| Always                                                   | Windows (and every `portable` check)                                                              | Length                                         |
|----------------------------------------------------------|---------------------------------------------------------------------------------------------------|------------------------------------------------|
| not empty or blank; not `.` or `..`; no `/`; no null byte | no `\` ; none of `< > : " \| ? *` ; no control characters; no trailing dot or space; not a device name (`CON`, `NUL`, `COM1`…`LPT9`, with any extension) | at most 255 bytes (POSIX) / 255 UTF-16 units (Windows) |

**Example usage:**

```python
is_valid_filename("report.md")         # -> True
is_valid_filename("what?.md")          # -> False  ('?' is forbidden on Windows)
is_valid_filename("CON.txt")           # -> False  (reserved device name)
is_valid_filename("a/b")               # -> False  (a path, not a name)
is_valid_filename("a:b", portable=False)   # -> True on Linux, False on Windows
```

**Under the hood:**

```python
return find_filename_problem(name, portable=portable) is None
```

`find_filename_problem(name, ...)` returns the *reason* as text
(`"contains the character '?', which Windows forbids in names"`), or `None`. The same
function feeds the [`IsValidFilename`](../README_PATH_RULES.md#isvalidfilename) rule's
failure card, so the rule can never reject a name for one reason and explain it with
another. Not checked: whether the name exists, and the total path length (Windows
`MAX_PATH`).

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicchecks--predicates-that-never-raise)
