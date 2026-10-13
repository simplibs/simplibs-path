# 🧭 `simplibs-path`

[![PyPI](https://img.shields.io/pypi/v/simplibs-path)](https://pypi.org/project/simplibs-path/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-path/blob/main/LICENSE)

**Paths you can trust — normalize, check, ensure and scan, without surprises.**

A Python library for everyday work with paths and directory trees, built around one
idea: every operation exists first as a plain, well-behaved **function**, and is then
offered as a composable **`Rule`** (for filters and validation) and as a pipeline
**`Action`** (for chained processing). Predicates never raise for disk problems,
operations that fail explain exactly why through structured
[`simplibs-exception`](https://pypi.org/project/simplibs-exception/) cards, and the
defaults are the safe ones — symlink-aware, Windows-aware, nothing silently hidden.

```python
from simplibs.path import collect_files, rebase_path, ensure_parent_dir
from simplibs.path.rules import HasSuffix, IsHidden

# Select by rule, map to an output location, prepare its folder
sources = collect_files("~/project", include_filter=HasSuffix(".py") & ~IsHidden())
target  = rebase_path(sources[0], source_root="~/project", target_root="out", new_suffix=".md")
ensure_parent_dir(target)
```

> `simplibs-path` is the first building block for file-processing pipelines in the
> ecosystem. Its `Rule`s are built on [`simplibs-rules`](https://pypi.org/project/simplibs-rules/),
> its `Action`s on [`simplibs-actions`](https://pypi.org/project/simplibs-actions/).
> You can use the plain functions without ever touching either.

---

## 🧭 The Core Philosophy

Path handling in Python is easy until it is not: a blank string quietly means "the
current directory", `os.access` lies on Windows, a symlink loop turns a recursive scan
into an endless one, `.gitignore`-style folders drown the result, and a "check" that
opens a file for writing leaves an empty file behind. `simplibs-path` takes those
traps seriously:

* **Functions first.** All logic lives in small, independent, reusable functions.
  Rules and actions are thin layers over them — never a second copy of the logic.
* **Predicates answer, they do not throw.** `is_path_writable`, `is_within`,
  `IsFile()` and friends return a plain `bool` for anything the disk can refuse.
* **Operations explain themselves.** `ensure_dir`, `collect_paths` and the others raise
  structured, actionable errors (`NotFoundError`, `StateError`, `AccessError`,
  `ParamError`) instead of leaking a bare `OSError`.
* **Safe defaults.** Symlinks are resolved, links and junctions are never entered
  during a scan, version-control and cache folders are skipped, and path-traversal is
  one call away (`is_within`).
* **Honest about time.** A filesystem answer is true *now*; the docs say where a check
  is a fail-fast message rather than a guarantee.

---

## 📦 Installation

```bash
pip install simplibs-path
```

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Plain functions

```python
from simplibs.path import normalize_path, collect_files, ensure_dir

root = normalize_path("~/project")            # absolute, ~ expanded, symlinks resolved
files = collect_files(root)                   # sorted list of Path objects
ensure_dir(root / "out" / "reports")          # created, with its parents, if missing
```

### Level 2: Rules as filters and gates

```python
from simplibs.path import collect_files
from simplibs.path.rules import HasSuffix, IsHidden, IsFile, IsWithin

wanted = HasSuffix(".py", ".md") & ~IsHidden()
collect_files("~/project", include_filter=wanted)

wanted.describe()          # -> "suffix one of '.py', '.md' & not hidden path"
IsWithin("out").is_valid("out/reports/a.md")     # -> True
IsWithin("out").is_valid("out/../secret.txt")    # -> False
```

### Level 3: Actions as pipeline steps

```python
from simplibs.path.actions import CollectFiles, FilterPaths
from simplibs.path.rules import IsDir, HasSuffix, IsHidden

pipeline = (
    IsDir()                                              # a Rule becomes a guard step
    >> CollectFiles(include_filter=HasSuffix(".py"))
    >> FilterPaths(rule=~IsHidden())
)

pipeline("~/project")                  # -> [Path(...), Path(...), ...]
await pipeline.acall("~/project")      # the same, off the event loop
```

### Level 4: Safety helpers

```python
from simplibs.path import is_within, is_valid_filename, make_unique_path

is_within(target, "out")                 # symlink-safe containment check
is_valid_filename("what?.md")            # -> False ('?' is forbidden on Windows)
make_unique_path("out/report.md")        # -> out/report (1).md, if the name is taken
```

---

## 🛠️ Architecture & Package Structure

```
src/simplibs/path/
├── logic/                ◄── The functional core — plain functions, no Rule/Action knowledge
│   ├── transformers/     ◄── normalize_path, normalize_entry_path, rebase_path, relativize_path, change_suffix, make_unique_path
│   ├── checks/           ◄── is_empty_dir, is_hidden_path, is_path_readable, is_path_writable, is_valid_filename, is_within
│   ├── ensure/           ◄── ensure_dir, ensure_file, ensure_parent_dir
│   └── scanners/         ◄── collect_paths, collect_files, collect_dirs, iter_paths, filter_paths, ignore_names
├── rules/                ◄── Rule classes over the functions (domain folder)
│   ├── lexical/          ◄── Judge a path by its text — HasSuffix, NameIs, StemIs, ParentNameIs, IsAbsolutePath, ...
│   └── filesystem/       ◄── Ask the disk — PathExists, IsFile, IsDir, IsSymlink, IsEmptyDir, ...
├── actions/              ◄── Action classes over the functions (domain folder)
└── annotations/          ◄── Shared types — PathLike, PathPredicate, RecursionDepth
```

Everything in `logic/` and the three public types is importable straight from
`simplibs.path`. `rules` and `actions` are separate domains, imported through their own
folders:

```python
from simplibs.path import collect_files, PathLike                  # functions and types
from simplibs.path.rules import HasSuffix, IsFile                  # rules
from simplibs.path.actions import CollectFiles, RebasePath         # actions
```

---

## 🔄 `logic/transformers/` — Path in, path out

Pure path arithmetic: nothing here changes the disk (`make_unique_path` only *looks*).

| Function               | Description / Parameters                                                                                             |
|------------------------|----------------------------------------------------------------------------------------------------------------------|
| `normalize_path`       | Absolute, `~`-expanded, collapsed path (`path`, `resolve_symlinks=True`). The path does not have to exist.           |
| `normalize_entry_path` | Resolves the containing directory while preserving the final path name, even if it is a symlink (`path`). |
| `rebase_path`          | Maps a path from one root to the same place under another (`path`, `source_root`, `target_root`, `new_suffix=None`). |
| `relativize_path`      | Expresses a path relative to a root (`path`, `root`).                                                                |
| `change_suffix`        | Replaces, adds or removes the last suffix (`path`, `new_suffix`).                                                    |
| `make_unique_path`     | Returns the path, or a numbered variant (`name (1).ext`) that does not exist yet (`path`, `max_attempts=1000`).      |

➡️ [README_PATH_TRANSFORMERS](https://github.com/simplibs/simplibs-path/blob/main/docs/logic/README_PATH_TRANSFORMERS.md)

---

## ✅ `logic/checks/` — Predicates that never raise

Each returns a `bool` and treats any refusal by the operating system as `False`.
Checks that are a single `pathlib` call (`exists`, `is_file`, `is_dir`, ...) have no
function here — only their rule.

| Function            | Description / Parameters                                                                                       |
|---------------------|----------------------------------------------------------------------------------------------------------------|
| `is_path_readable`  | A file that can be opened, or a directory that can be listed (`path`).                                         |
| `is_path_writable`  | Could be written to *now*, without creating or changing anything (`path`).                                     |
| `is_empty_dir`      | An existing, listable directory with no entries (`path`).                                                      |
| `is_hidden_path`    | The final name starts with a dot; optionally the Windows attribute (`path`, `check_attributes=False`).         |
| `is_within`         | The path lies inside a root — symlink-safe path-traversal guard (`path`, `root`, `resolve_symlinks=True`, `allow_equal=True`). |
| `is_valid_filename` | A string usable as a file name; portable across Windows and POSIX by default (`name`, `portable=True`).        |

➡️ [README_PATH_CHECKS](https://github.com/simplibs/simplibs-path/blob/main/docs/logic/README_PATH_CHECKS.md)

---

## 🏗️ `logic/ensure/` — Make a state true

The functions that change the disk. Each returns the normalized path, so it chains.

| Function            | Description / Parameters                                                              |
|---------------------|---------------------------------------------------------------------------------------|
| `ensure_dir`        | Guarantees a directory exists, creating its parents too (`path`).                     |
| `ensure_file`       | Guarantees a file exists, optionally creating it and its folder (`path`, `create=True`). |
| `ensure_parent_dir` | Guarantees the folder a path lives in exists; returns the path itself (`path`).        |

➡️ [README_PATH_ENSURE](https://github.com/simplibs/simplibs-path/blob/main/docs/logic/README_PATH_ENSURE.md)

---

## 🔍 `logic/scanners/` — Look at a directory tree

| Function        | Description / Parameters                                                                                     |
|-----------------|--------------------------------------------------------------------------------------------------------------|
| `collect_paths` | Sorted list of files and/or directories (`root_dir`, `recursive`, `include_filter`, `exclude_filter`, `ignore_names`, `collect_files`, `collect_dirs`). |
| `collect_files` | Files only — the same options without the type flags.                                                        |
| `collect_dirs`  | Directories only — the same options without the type flags.                                                  |
| `iter_paths`    | The lazy, unsorted counterpart of `collect_paths` — results as they are found.                               |
| `filter_paths`  | Keeps the paths of a list that satisfy a `Rule` or callable (`paths`, `rule`).                               |

Scans skip `.git`, `__pycache__`, `node_modules`, virtual environments, IDE folders and
OS housekeeping files by default (`DEFAULT_IGNORE_NAMES`). Ambiguous folder names such as
`build` or `dist` are opt-in (`IGNORE_GENERIC`).

| Constant               | Description                                                                |
|------------------------|----------------------------------------------------------------------------|
| `DEFAULT_IGNORE_NAMES` | Union of the groups below, without `IGNORE_GENERIC` — the scanners' default. |
| `IGNORE_VCS`           | Version control metadata (`.git`, `.svn`, ...).                            |
| `IGNORE_ENV`           | Virtual environments, installed dependencies, `.env`.                      |
| `IGNORE_BUILD`         | Caches and tool output with unmistakable names (`__pycache__`, `*.egg-info`, ...). |
| `IGNORE_IDE`           | Editor and IDE settings.                                                   |
| `IGNORE_SYSTEM`        | OS housekeeping (`.DS_Store`, `Thumbs.db`, ...).                           |
| `IGNORE_GENERIC`       | `build`, `dist`, `site`, `env`, ... — opt-in, because they are also normal folder names. |

➡️ [README_PATH_SCANNERS](https://github.com/simplibs/simplibs-path/blob/main/docs/logic/README_PATH_SCANNERS.md)

---

## 📐 `rules/` — Rules for paths

Every rule is a `Rule` from [`simplibs-rules`](https://pypi.org/project/simplibs-rules/):
composable with `&`, `|` and `~`, usable as a scanner filter, as a `@validate_call`
annotation (`validated_type(Path, IsDir())`) and as a pipeline gate (`IsDir() >> ...`).

### `lexical/` — Judge a path by its text (cheap, no disk access)

| Class             | Description / Parameters                                                                            |
|-------------------|-----------------------------------------------------------------------------------------------------|
| `HasSuffix`       | The name ends with one of the suffixes (`*suffixes`, `ignore_case=True`). `HasSuffix("")` = no suffix. |
| `NameIs`          | The final name satisfies another rule (`rule`) — any string rule, pointed at the name.              |
| `StemIs`          | The name without its last suffix satisfies another rule (`rule`).                                   |
| `ParentNameIs`    | The containing folder's name satisfies another rule (`rule`).                                       |
| `IsAbsolutePath`  | The path is absolute.                                                                               |
| `IsRelativePath`  | The path is relative.                                                                               |
| `IsHidden`        | The final name starts with a dot (`check_attributes=False`).                                        |
| `IsWithin`        | The path lies inside a root (`root`, `resolve_symlinks=True`, `allow_equal=True`).                  |
| `IsValidFilename` | A string — or a `Path`'s final name — is usable as a file name (`portable=True`).                   |

### `filesystem/` — Ask the disk

| Class            | Description                                                   |
|------------------|---------------------------------------------------------------|
| `PathExists`     | Something exists at the path.                                 |
| `IsFile`         | An existing regular file (or a symlink to one).               |
| `IsDir`          | An existing directory (or a symlink to one).                  |
| `IsSymlink`      | The path itself is a symbolic link, working or broken.        |
| `IsEmptyDir`     | An existing directory with no entries.                        |
| `IsEmptyFile`    | An existing regular file of size zero.                        |
| `IsPathReadable` | A file that can be read, or a directory that can be listed.   |
| `IsPathWritable` | Could be written to now, with no side effects.                |

➡️ [README_PATH_RULES](https://github.com/simplibs/simplibs-path/blob/main/docs/README_PATH_RULES.md)

---

## ⚙️ `actions/` — Pipeline steps

Every function that takes one main value and returns one result is also an `Action` from
[`simplibs-actions`](https://pypi.org/project/simplibs-actions/): configured once, called
with the main input, chainable with `>>`, `&` and `|`, and awaitable through `acall`.

| Action               | Wraps                  | Main input → result                |
|----------------------|------------------------|------------------------------------|
| `NormalizePath`      | `normalize_path`       | path → `Path`                      |
| `NormalizeEntryPath` | `normalize_entry_path` | path → `Path`                      |
| `RebasePath`         | `rebase_path`          | path → `Path`                      |
| `RelativizePath`     | `relativize_path`      | path → `Path`                      |
| `ChangeSuffix`       | `change_suffix`        | path → `Path`                      |
| `MakeUniquePath`     | `make_unique_path`     | path → `Path`                      |
| `EnsureDir`          | `ensure_dir`           | path → `Path`                      |
| `EnsureFile`         | `ensure_file`          | path → `Path`                      |
| `EnsureParentDir`    | `ensure_parent_dir`    | path → `Path`                      |
| `CollectPaths`       | `collect_paths`        | root → `list[Path]`                |
| `CollectFiles`       | `collect_files`        | root → `list[Path]`                |
| `CollectDirs`        | `collect_dirs`         | root → `list[Path]`                |
| `FilterPaths`        | `filter_paths`         | `list[Path]` → `list[Path]`        |

Predicates and `iter_paths` have no action: a `Rule` is already a valid pipeline step
(it becomes a pass-through gate), and a generator does not fit a one-value-in,
one-value-out model.

➡️ [README_PATH_ACTIONS](https://github.com/simplibs/simplibs-path/blob/main/docs/README_PATH_ACTIONS.md)

---

## 🏷️ `annotations/` — Shared validatable annotations

| Type             | Description                                                                                    |
|------------------|------------------------------------------------------------------------------------------------|
| `PathLike`       | A non-blank string or a `Path`. Rejects `""`, which `Path` would silently turn into `.`.       |
| `PathPredicate`  | A `(Path) -> bool` callable — a function, a lambda, or any `Rule`.                             |
| `RecursionDepth` | `True`/`False` or a non-negative `int` — how deep a scan may go.                               |

Use them in your own signatures so your functions accept exactly what this library does.

➡️ [README_PATH_ANNOTATIONS](https://github.com/simplibs/simplibs-path/blob/main/docs/README_PATH_ANNOTATIONS.md)

---

## 🪟 Platform Notes

The library is written for Windows and POSIX alike, and where they differ it says so:

* **Symlinks and junctions** are followed when a path is normalized, but never *entered*
  during a scan — so link cycles cannot trap it. On Windows this includes directory
  junctions (`mklink /J`), which `is_symlink()` alone does not detect.
* **Case:** names compare case-insensitively on Windows and case-sensitively elsewhere
  (`ignore_names`, `Path` ordering).
* **File names:** `is_valid_filename` is *portable by default* — it rejects names that
  only Windows refuses (`con`, `a:b`, `name.`) so that generated files can be copied
  anywhere.
* **Permissions:** a check such as `is_path_writable` actually probes the target, because
  `os.access` ignores ACLs and read-only attributes on Windows.

---

## ⚠️ Exceptions

Functions raise structured [`simplibs.exception`](https://pypi.org/project/simplibs-exception/)
cards rather than bare `OSError`s:

| Exception         | Raised when                                                                         |
|-------------------|-------------------------------------------------------------------------------------|
| `ValidationError` | An argument has the wrong type or shape (e.g. a blank path) — via `validate_call`.  |
| `ParamError`      | An argument combination is unusable (path outside its root, both collect flags off, a malformed suffix). |
| `NotFoundError`   | A required path or scan root does not exist.                                        |
| `StateError`      | The filesystem is in the wrong state (a file where a directory is needed, ...).     |
| `AccessError`     | The operating system refused (permissions, unresolvable path).                      |
| `OperationError`  | An operation ran out of options (no free numbered name left).                       |

Predicates (`checks/`, `rules/`) never raise for disk problems — they return `False`.

---

## 🔗 Related libraries

* **[`simplibs-rules`](https://pypi.org/project/simplibs-rules/)** — the `Rule` engine behind `simplibs.path.rules`.
* **[`simplibs-actions`](https://pypi.org/project/simplibs-actions/)** — the `Action` abstraction and containers behind `simplibs.path.actions`.
* **[`simplibs-validate`](https://pypi.org/project/simplibs-validate/)** — `@validate_call`, which validates every function argument here.
* **[`simplibs-exception`](https://pypi.org/project/simplibs-exception/)** — the structured exception cards.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---
