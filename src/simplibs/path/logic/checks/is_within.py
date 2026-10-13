import os
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import to_path

@validate_call
def is_within(
    path: PathLike,
    root: PathLike,
    *,
    resolve_symlinks: bool = True,
    allow_equal: bool = True,
    _validate_call: bool = True,
) -> bool:
    """Check whether a path lies inside a root directory, without touching its content.

    Args:
        path: The path to test.
        root: The directory it is supposed to be inside.
        resolve_symlinks: If True (default), symlinks and `..` are resolved
            before comparing, so a link pointing out of `root` does not
            count as inside. If False, the comparison is purely lexical.
        allow_equal: Whether a path equal to `root` itself counts as inside.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True if `path` is inside `root` (or equal to it, when allowed).
        Never raises for unresolvable input — that is simply False.
    """

    # 1. Anything that cannot be turned into a path is not inside anything
    candidate = to_path(path)
    base = to_path(root)
    if candidate is None or base is None:
        return False

    # 2. Make both absolute the same way
    try:

        # 2.1 Follow symlinks and collapse ".." through the real filesystem
        if resolve_symlinks:
            candidate = candidate.resolve()
            base = base.resolve()

        # 2.2 Purely lexical — absolute and collapsed, symlinks untouched
        else:
            candidate = Path(os.path.abspath(candidate))
            base = Path(os.path.abspath(base))

    # 3. Paths that cannot be resolved cannot be proven inside
    except (OSError, RuntimeError, ValueError):
        return False

    # 4. Equal paths are decided by the flag, everything else by containment
    if candidate == base:
        return allow_equal
    return candidate.is_relative_to(base)


_DESIGN_NOTES = """
# is_within — Containment Without String Tricks

## Purpose
The guard against path traversal ("`../../etc/passwd` must not leave the
output folder") and the predicate behind `IsWithin`.

---

## 1. Why Not `str(path).startswith(str(root))`
`/data/src2` starts with `/data/src` but is not inside it, `..` segments
hide an escape, and Windows compares case-insensitively. `Path.is_relative_to`
on normalized absolute paths compares whole path *parts*, with the right
case rules for the platform.

## 2. Safe by Default: Symlinks Are Resolved
A symlink inside `root` that points outside it must not pass. Resolving both
sides handles that. The cost is a few syscalls per call, so
`resolve_symlinks=False` exists for filters over paths that `collect_paths`
already produced in normalized form.

## 3. Unresolvable Means False
A security check that raises can be skipped by a broad `except`; one that
answers `False` fails closed.
"""
