from pathlib import Path
from typing import Any


def to_path(value: Any) -> Path | None:
    """Turn a path candidate into a `Path` without touching the disk, or return None.

    Used by every rule, which must never raise on a bad input — a value
    that cannot be a path simply fails the rule.

    Args:
        value: Any value; only a `str` or a `Path` is a path candidate.

    Returns:
        The `Path` with a leading `~` expanded, or `None` if `value` is not
        a `str`/`Path`, is blank, contains a null byte, or cannot be
        expanded.
    """

    # 1. Only str and Path instances are path candidates
    if not isinstance(value, (str, Path)):
        return None

    # 2. A blank string would silently become the current directory
    if isinstance(value, str) and not value.strip():
        return None

    # 3. A null byte makes every later filesystem call raise ValueError
    if "\0" in str(value):
        return None

    # 4. Expand "~" — pure string work, no stat/resolve syscalls
    try:
        return Path(value).expanduser()

    # 5. "~unknown_user" or another unusable value — not a path
    except (RuntimeError, OSError, ValueError):
        return None


_DESIGN_NOTES = """
# to_path — the one safe str/Path → Path conversion

## Purpose
`Rule.is_valid` must never raise, and every path rule starts the same way:
"is this even a path, and which one?". `to_path` is that shared first step,
so no rule repeats the `isinstance` / blank / null-byte / `expanduser`
dance.

---

## 1. Returns None Instead of Raising

The caller decides what a non-path means: a rule answers `False` (and its
`build_exception` reports a type problem), a function would have been
rejected earlier by the `PathLike` annotation.

## 2. Why Only `expanduser`, Never `resolve`

Rules run inside filters over thousands of entries. `resolve()` is a
syscall per call and follows symlinks; `expanduser()` is string work. The
entries produced by `collect_paths` are already absolute and normalized, so
nothing more is needed — while a user-typed `~/project` still means what
they expect.

## 3. Why the Null-Byte Check Is Explicit

`Path("a\\0b")` constructs fine; the `ValueError: embedded null byte` only
appears later, at the first `stat`/`open`. Catching it here keeps that
failure out of every rule's `is_valid`.

## 4. `~unknown_user`

On POSIX `Path("~unknown").expanduser()` raises `RuntimeError`; on Windows it
is expanded to a sibling of the home directory. Both outcomes are handled:
a `RuntimeError` becomes `None`, a successful expansion is returned.
"""
