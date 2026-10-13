import os
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
from ..transformers import normalize_path
# Inners
from ._validations import raise_ensure_dir_error, raise_ensure_dir_not_a_dir_error


@validate_call
def ensure_dir(
    path: PathLike,
) -> Path:
    """Guarantee that a directory exists, creating it (and any missing
    parents) if necessary.

    Args:
        path: The directory path to guarantee.

    Returns:
        The normalized, guaranteed-to-exist directory `Path`.

    Raises:
        StateError: If something that is not a directory (a file) already
            occupies the path.
        AccessError: If the directory cannot be created due to
            insufficient permissions or another OS-level failure.
    """

    # 1. Normalize the target path
    normalized_path = normalize_path(path)

    # 2. Already exists — must be a directory, not a file
    if normalized_path.exists():
        if not normalized_path.is_dir():
            raise_ensure_dir_not_a_dir_error(normalized_path)
        return normalized_path

    # 3. Create the directory (and parents) if missing
    try:
        normalized_path.mkdir(parents=True, exist_ok=True)

    # 4. Creation failed
    except OSError as caught_exc:

        # 4.1 Something else took the name meanwhile (a file created in the
        #     gap since step 2) — a state problem, not a permission problem
        if os.path.lexists(normalized_path) and not normalized_path.is_dir():
            raise_ensure_dir_not_a_dir_error(normalized_path)

        # 4.2 Permissions, a read-only disk, a file in the parent chain, ...
        raise_ensure_dir_error(normalized_path, caught_exc)

    # 5. Return the guaranteed directory
    return normalized_path


_DESIGN_NOTES = """
# ensure_dir — "This Directory Exists Now"

## Purpose
Turns "I need this folder" into one step that either succeeds or explains
why not. Returns the normalized path, so it chains
(`NormalizePath >> EnsureDir >> CollectFiles`).

---

## 1. Moved From `validators/`, Two Small Corrections
* `except (PermissionError, OSError)` is now `except OSError` —
  `PermissionError` is a subclass, the tuple said nothing extra.
* The race "a file appeared between the check and `mkdir`" used to surface
  as `AccessError` with a how-to-fix about permissions. It is now reported
  as the `StateError` it really is (step 4.1).

## 2. A Symlink Is Followed
`normalize_path` resolves symlinks first, so `ensure_dir("link")` for a
dangling link creates the directory the link *points to*. That is the
consistent meaning of "this path" everywhere in the library.

## 3. Idempotent
Calling it on an existing directory touches nothing and costs one `stat`.
"""
