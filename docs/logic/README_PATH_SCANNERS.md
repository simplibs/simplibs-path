# 🔍 `logic/scanners` — Look at a Directory Tree

The `scanners` package holds everything that *looks at* a directory tree without changing
it: collecting the files and directories inside a root, walking them lazily, and filtering
a list of paths. All of it sits on one shared walker built on `os.scandir`, so the rules
below hold for every function alike.

```python
from simplibs.path import collect_files, collect_paths, iter_paths, filter_paths
```

## How a scan behaves

* **What is collected.** Files and directories — and symlinks *to* them, reported as what
  they point to. Broken symlinks and special files (FIFOs, sockets, devices) are **never**
  collected.
* **What is entered.** Real directories only. A symlinked directory is reported but never
  entered, and on Windows neither is a directory junction — so a link cycle cannot trap a
  scan, and a link cannot lead it out of the tree.
* **What is skipped.** Names matching `ignore_names` (files *and* directories — an ignored
  directory is not entered at all). The default is [`DEFAULT_IGNORE_NAMES`](#ignore_names--what-a-scan-skips).
* **What happens to errors.** An unreadable *sub*directory is skipped silently — a normal
  tree contains a few. An unreadable, missing or non-directory *root* is an error
  (`AccessError`, `NotFoundError`, `StateError`), because skipping it would return an empty
  result that looks exactly like "nothing found". Both type flags off is a `ParamError`.
* **What the paths look like.** Absolute: the normalized root joined with the relative
  part. The root itself is never included.

## A note on filters

`include_filter` and `exclude_filter` take a [`PathPredicate`](../README_PATH_ANNOTATIONS.md#pathpredicate)
— a function, a lambda or any [`Rule`](../README_PATH_RULES.md). Two things to know:

* **`exclude_filter` wins** over `include_filter` (it is checked first).
* **Filters do not prune.** Excluding a *directory* hides that entry, but its contents are
  still walked and judged on their own. Only `ignore_names` prunes a subtree. This is
  deliberate — a filter on a directory says nothing about its children.

## A note on `recursive`

| Value        | Meaning                                                        |
|--------------|----------------------------------------------------------------|
| `True`       | Unlimited depth (the default).                                 |
| `False`      | Only the root's own entries (depth 0).                         |
| `0`, `1`, … | A maximum depth: `0` = the root's own entries, `1` = one level deeper, … |

## A note on `Collection` instead of `Iterable`

`ignore_names` and `filter_paths(paths)` take a **collection** (list, tuple, set,
frozenset), not an arbitrary iterable. `@validate_call` checks `Iterable[...]` by
iterating it — which would silently exhaust a generator before the function ever saw it.
A generator is therefore rejected with a clear `ValidationError`; wrap it in `list(...)`.
A bare **string** for `ignore_names` is rejected too (it would be split into characters).

---

## 🧭 Table of Contents

* [`collect_paths`](#collect_paths)
* [`collect_files`](#collect_files)
* [`collect_dirs`](#collect_dirs)
* [`iter_paths`](#iter_paths)
* [`filter_paths`](#filter_paths)
* [`ignore_names` — what a scan skips](#ignore_names--what-a-scan-skips)

[⬅️ Back to main README](../../README.md#-logicscanners--look-at-a-directory-tree)

---

### `collect_paths`

Scans a directory tree and collects the matching paths into a **sorted list**.

**Parameters:**

* `root_dir` (*PathLike*): The root directory to scan.
* `recursive` (*RecursionDepth*, keyword-only, default `True`): `True`, `False` or a
  maximum depth (see above).
* `include_filter` (*PathPredicate | None*, keyword-only, default `None`): A path must
  satisfy it to be collected.
* `exclude_filter` (*PathPredicate | None*, keyword-only, default `None`): A path that
  satisfies it is skipped (checked first).
* `ignore_names` (*Collection[str] | None*, keyword-only, default `DEFAULT_IGNORE_NAMES`):
  Entry names or glob patterns to skip entirely. `None` ignores nothing.
* `collect_files` (*bool*, keyword-only, default `True`): Collect files.
* `collect_dirs` (*bool*, keyword-only, default `False`): Collect directories.

**Returns:**

* `list[Path]`: Absolute paths, sorted **by path parts** — a directory's contents sort right
  after the directory itself (tree order), and on Windows case-insensitively, as Explorer
  lists a folder.

**Raises:**

* `ParamError`: Both `collect_files` and `collect_dirs` are `False`, or `ignore_names` is a
  bare string.
* `NotFoundError`: `root_dir` does not exist.
* `StateError`: `root_dir` is not a directory.
* `AccessError`: `root_dir` cannot be listed.

**Example usage:**

```python
collect_paths("project")                                   # files, default ignores
collect_paths("project", collect_dirs=True)                # files and directories
collect_paths("project", recursive=1)                      # root + one level down
collect_paths("project", include_filter=lambda p: p.suffix == ".py")

# Rules compose into filters
collect_paths("project", include_filter=HasSuffix(".py") & ~IsHidden())

# Extend the default ignore list instead of replacing it
collect_paths("project", ignore_names=DEFAULT_IGNORE_NAMES | {"fixtures"})
```

**Under the hood:**

```python
@validate_call
def collect_paths(root_dir, *, recursive=True, include_filter=None, exclude_filter=None,
                  ignore_names=DEFAULT_IGNORE_NAMES, collect_files=True,
                  collect_dirs=False) -> list[Path]:
    return sorted(scan_paths(root_dir, recursive=recursive, ...))
```

`scan_paths` (internal) does all checks and preparation **when called** — both flags,
the root (exists, is a directory, can be listed), the depth, the ignore matcher and the
filters resolved once — and returns a lazy generator. All four scanner functions share it,
so each validates its arguments exactly once.

[▲ Back to top](#-table-of-contents)

---

### `collect_files`

Collects only the **files** of a tree into a sorted list — `collect_paths` with the type
flags fixed.

**Parameters:**

* `root_dir`, `recursive`, `include_filter`, `exclude_filter`, `ignore_names` — exactly as
  in [`collect_paths`](#collect_paths). The type flags are **not** parameters.

**Returns:**

* `list[Path]`: The matching absolute file paths, sorted.

**Example usage:**

```python
collect_files("project", include_filter=HasSuffix(".py", ".md"))
```

**Under the hood:**

```python
return sorted(scan_paths(root_dir, ..., collect_files=True, collect_dirs=False))
```

It is a real function rather than a `functools.partial` of `collect_paths`: a partial
only changes the *defaults*, so `collect_dirs=True` could still be passed. With the flags
gone from the signature, the [`CollectFiles`](../README_PATH_ACTIONS.md#collectfiles)
action built on it is genuinely locked.

[▲ Back to top](#-table-of-contents)

---

### `collect_dirs`

Collects only the **directories** of a tree into a sorted list — `collect_paths` with the
type flags fixed. The root itself is not included.

**Parameters:**

* `root_dir`, `recursive`, `include_filter`, `exclude_filter`, `ignore_names` — as in
  [`collect_paths`](#collect_paths).

**Returns:**

* `list[Path]`: The matching absolute directory paths, sorted.

**Example usage:**

```python
collect_dirs("project", recursive=2)                       # folders up to two levels deep
collect_dirs("project", exclude_filter=NameIs(StartsWith("_")))
```

**Under the hood:**

```python
return sorted(scan_paths(root_dir, ..., collect_files=False, collect_dirs=True))
```

[▲ Back to top](#-table-of-contents)

---

### `iter_paths`

The **lazy** sibling of `collect_paths`: yields paths as they are found, so a huge tree can
be processed as it is discovered and the walk can be stopped early.

**Parameters:**

* Identical to [`collect_paths`](#collect_paths).

**Returns:**

* `Iterator[Path]`: A lazy iterator of absolute paths — **not sorted**, in no promised
  order. Anything that needs a stable order uses `collect_paths`.

**Raises:**

* The same as `collect_paths` — and they are raised **when `iter_paths` is called**, not at
  the first `next()`.

**Example usage:**

```python
for path in iter_paths("huge_tree", include_filter=HasSuffix(".log")):
    if is_interesting(path):
        break                                   # the rest of the tree is never walked

first = next(iter_paths("project"))
```

**Under the hood:**

```python
@validate_call
def iter_paths(root_dir, *, ...) -> Iterator[Path]:
    return scan_paths(root_dir, ...)            # prepared now, walked lazily
```

`iter_paths` is an ordinary function that *returns* a generator, not a generator function.
A generator function would run none of its body — including the root checks — until the
first `next()`, so a typo in the path would surface far away from the mistake. There is no
`Action` counterpart: a generator is consumed once and cannot be logged or re-run by the
action machinery.

[▲ Back to top](#-table-of-contents)

---

### `filter_paths`

Keeps the paths of a list that satisfy a `Rule` or callable — filtering a list you already
have, such as the result of an earlier pipeline step.

**Parameters:**

* `paths` (*Collection[Path]*): A list, tuple or set of paths (not a generator).
* `rule` (*PathPredicate*): A `Rule` or `(Path) -> bool` callable. **Required.**

**Returns:**

* `list[Path]`: A new list with the paths satisfying `rule`, in their original order.

**Example usage:**

```python
paths = collect_files("project")
filter_paths(paths, HasSuffix(".py"))
filter_paths(paths, lambda p: p.stat().st_size > 1_000_000)
```

**Under the hood:**

```python
predicate = as_path_predicate(rule)              # a Rule becomes its bound is_valid
return [path for path in paths if predicate(path)]
```

`rule` is required because a filter without one would only copy the list. Exceptions
raised by the predicate propagate unchanged.

[▲ Back to top](#-table-of-contents)

---

### `ignore_names` — what a scan skips

Names that scanners skip, grouped into named, immutable `frozenset`s. **Names containing
`*`, `?` or `[` are glob patterns** (`*.egg-info`); all others match exactly, and matching
is case-insensitive on Windows. They apply to **files and directories** alike — `.DS_Store`
and `.env` are files.

```python
from simplibs.path import DEFAULT_IGNORE_NAMES, IGNORE_GENERIC, IGNORE_VCS

collect_files("project")                                         # DEFAULT_IGNORE_NAMES
collect_files("project", ignore_names=None)                      # nothing ignored
collect_files("project", ignore_names=DEFAULT_IGNORE_NAMES | IGNORE_GENERIC)
collect_files("project", ignore_names=IGNORE_VCS | {"fixtures"})
```

| Constant               | In `DEFAULT_IGNORE_NAMES` | Contents                                                                                                                                                                                   |
|------------------------|:-------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `IGNORE_VCS`           | ✅ | `.bzr` `.git` `.hg` `.svn`                                                                                                                                                                  |
| `IGNORE_ENV`           | ✅ | `.direnv` `.env` `.poetry` `.venv` `.virtualenv` `__pypackages__` `node_modules` `venv`                                                                                                     |
| `IGNORE_BUILD`         | ✅ | `*.egg-info` `.cache` `.coverage` `.coverage.*` `.eggs` `.gradle` `.hypothesis` `.ipynb_checkpoints` `.mypy_cache` `.next` `.nox` `.nuxt` `.pytest_cache` `.pytype` `.ruff_cache` `.serverless` `.terraform` `.tox` `__pycache__` `htmlcov` |
| `IGNORE_IDE`           | ✅ | `.fleet` `.idea` `.settings` `.vs` `.vscode`                                                                                                                                                |
| `IGNORE_SYSTEM`        | ✅ | `$RECYCLE.BIN` `.DS_Store` `.fseventsd` `.Spotlight-V100` `.TemporaryItems` `.Trashes` `System Volume Information` `Thumbs.db` `desktop.ini` `ehthumbs.db`                                  |
| `IGNORE_GENERIC`       | ❌ **opt-in** | `_build` `build` `dist` `env` `out` `site` `target`                                                                                                                                      |
| `DEFAULT_IGNORE_NAMES` | — | The union of the five ✅ groups. The scanners' default.                                                                                                                                       |

**Why `IGNORE_GENERIC` is opt-in.** `build/`, `dist/`, `site/` and `target/` are the output
folders of setuptools, MkDocs, Cargo and Maven — but `src/site/` or a package literally
named `env` exist too. A scan that hides them by default loses content without saying so,
which is worse than one that is a bit noisy. Dropping them is a conscious, one-expression
choice.

**Why `frozenset`.** A mutable default shared by every call could be changed by accident
and affect all later scans. A frozenset cannot, and `|` still builds a new, extended one.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../README.md#-logicscanners--look-at-a-directory-tree)
