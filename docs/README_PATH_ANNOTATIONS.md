# 🏷️ `annotations` — Shared Annotations

The `annotations` package holds the validatable annotations the whole library shares — the exact types the
functions, rules and actions declare for their parameters. They are exported from
`simplibs.path`, so **your own functions can accept exactly what this library accepts**:

```python
from simplibs.path import PathLike, PathPredicate, RecursionDepth
```

Each is a plain annotation object — no class to instantiate — and works with `simplibs-validate`
(`@validate_call`), with type checkers, and with `IsTyping`.

```python
from simplibs.validate import validate_call
from simplibs.path import PathLike, collect_files

@validate_call
def count_files(root: PathLike) -> int:
    return len(collect_files(root))
```

> The package also contains `ScanEntry`, the scanners' internal result type. It never
> appears in a public signature and is not exported from `simplibs.path`.

---

## 🧭 Table of Contents

* [`PathLike`](#pathlike)
* [`PathPredicate`](#pathpredicate)
* [`RecursionDepth`](#recursiondepth)

[⬅️ Back to main README](../README.md#-annotations--shared-validatable-annotations)

---

### `PathLike`

A filesystem path given as a **non-blank string** or a `Path` instance — the annotation of
every path parameter in the library.

**Definition:**

```python
PathLike = str_not_blank | Path
```

**Accepts:** `"src/a.py"`, `"~"`, `"."`, `Path("src/a.py")`, `Path(".")`.

**Rejects:** `""`, `"   "`, `None`, numbers, `bytes`, lists.

**Example usage:**

```python
IsTyping(PathLike).is_valid("src")       # -> True
IsTyping(PathLike).is_valid("")          # -> False

normalize_path("")                       # raises ValidationError, not "the current directory"
```

**Why a blank string is rejected.** `Path("")` and `Path("   ")` do not fail — they quietly
become `.`, the current working directory. Without this guard `ensure_dir("")` would
"succeed" and `collect_paths("")` would scan whatever directory the process happens to run
in. Rejecting it at the boundary turns a silent surprise into an immediate, readable error.

**Why `str | Path`, not `os.PathLike`.** Every function normalizes through `Path` first.
Keeping the accepted input to the two types people actually pass keeps error messages short
and avoids bytes-based `os.PathLike` objects, which `Path` cannot represent.

[▲ Back to top](#-table-of-contents)

---

### `PathPredicate`

A `(Path) -> bool` callable: a function, a lambda, or any [`Rule`](README_PATH_RULES.md) —
the annotation of `include_filter`, `exclude_filter` and `filter_paths`' `rule`.

**Definition:**

```python
PathPredicate = Callable[[Path], bool]
```

**Accepts:** any callable — `lambda p: p.suffix == ".py"`, `Path.is_file`,
`HasSuffix(".py") & ~IsHidden()`.

**Rejects:** anything not callable (`42`, `"is_file"`, a `Path`).

**Example usage:**

```python
collect_files("project", include_filter=lambda p: p.suffix == ".py")
collect_files("project", include_filter=HasSuffix(".py") & ~IsHidden())     # a Rule
```

**Why a plain `Callable` and no special protocol.** Every `Rule` is already callable
(`Rule.__call__` forwards to `is_valid`), so rules fit this type directly. The type check
only confirms the object is callable — argument and return types are not inspected — and the
scanners resolve the predicate **once**, before the loop, unwrapping a `Rule` to its bound
`is_valid` so the per-entry call stays as cheap as possible.

[▲ Back to top](#-table-of-contents)

---

### `RecursionDepth`

How deep a directory scan may go: `True`, `False` or a non-negative integer.

**Definition:**

```python
RecursionDepth = Annotated[bool | int, is_bool | (is_int & ge(0))]
```

**Accepts:** `True`, `False`, `0`, `1`, `2`, ...

**Rejects:** negative integers, floats (`1.5`), strings, `None`.

| Value      | Meaning                                                              |
|------------|----------------------------------------------------------------------|
| `True`     | Unlimited depth.                                                     |
| `False`    | Only the root's own entries.                                         |
| `0`, `1`, … | A maximum depth: `0` = the root's own entries, `1` = one level deeper, … |

**Example usage:**

```python
collect_files("project", recursive=False)     # just the top level
collect_files("project", recursive=2)         # two levels down
collect_files("project", recursive=-1)        # raises ValidationError
```

**Why `bool | int`.** `True`/`False` are the readable spellings of "all" and "none", while an
integer is a precise limit. Inside the scanners `True` is told apart from `1` with an
*identity* check (`recursive is True`) — `1 == True` in Python, so an equality check would
turn "depth 1" into "unlimited".

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-annotations--shared-validatable-annotations)
