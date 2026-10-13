from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from .normalize_path import normalize_path
from ._validations import raise_path_not_within_root_error


@validate_call
def relativize_path(
    path: PathLike,
    *,
    root: PathLike,
) -> Path:
    """Express a path relative to a root directory.

    Args:
        path: The path to relativize.
        root: The directory the result is relative to.

    Returns:
        The path relative to `root` (`Path(".")` when both are the same).

    Raises:
        ParamError: If `path` is not located inside `root`.
        AccessError: If either path cannot be normalized.
    """

    # 1. Normalize both paths the same way, so they are comparable
    normalized_path = normalize_path(path)
    normalized_root = normalize_path(root)

    # 2. Express the path relative to the root
    try:
        return normalized_path.relative_to(normalized_root)

    # 3. Not inside the root — report it instead of a bare pathlib error
    except ValueError:
        raise_path_not_within_root_error(normalized_path, normalized_root)


_DESIGN_NOTES = """
# relativize_path — Path Relative to a Root

## Purpose
Shows a collected path as it appears inside the scanned tree
(`src/a/b.py`, not `/home/me/project/src/a/b.py`) — for reports, logs and
as the first half of `rebase_path`.

## Why Both Sides Are Normalized
`Path.relative_to` compares path parts textually. `./src` vs `/abs/src`, or
a symlinked vs. a resolved root, would wrongly fail. Normalizing both with
the same function removes that class of surprise (and makes Windows'
case-insensitive comparison apply to real, absolute parts).
"""
