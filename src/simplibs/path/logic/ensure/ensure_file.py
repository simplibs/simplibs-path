import os
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
from ..transformers import normalize_path
# Inners
from .ensure_dir import ensure_dir
from ._validations import (
    raise_ensure_file_create_error,
    raise_ensure_file_not_a_file_error,
    raise_ensure_file_not_found_error,
)


@validate_call
def ensure_file(
    path: PathLike,
    *,
    create: bool = True,
) -> Path:
    """Guarantee that a path points to a file, optionally creating it
    (and its parent directory) if missing.

    Args:
        path: The file path to guarantee.
        create: If True (default), create the file and its parent
            directory when missing. If False, a missing file raises
            instead.

    Returns:
        The normalized, guaranteed-to-exist file `Path`.

    Raises:
        StateError: If the path exists but is a directory instead of a
            file, or a parent in the chain is a file.
        NotFoundError: If the file is missing and `create=False`.
        AccessError: If the file cannot be created due to missing permissions
            or an OS-level failure.
    """

    # 1. Normalize the target path
    normalized_path = normalize_path(path)

    # 2. Already exists — must be a file, not a directory
    if normalized_path.exists():
        if not normalized_path.is_file():
            raise_ensure_file_not_a_file_error(normalized_path)
        return normalized_path

    # 3. Missing, and creation was not requested
    if not create:
        raise_ensure_file_not_found_error(normalized_path)

    # 4. Missing, creation requested — guarantee the parent directory first
    ensure_dir(normalized_path.parent)

    # 5. Create the empty file
    try:
        normalized_path.touch(exist_ok=True)

    # 6. Creation failed
    except OSError as caught_exc:

        # 6.1 A directory took the name meanwhile (created in the gap since step 2)
        if os.path.lexists(normalized_path) and not normalized_path.is_file():
            raise_ensure_file_not_a_file_error(normalized_path)

        # 6.2 Permissions, a read-only disk, ...
        raise_ensure_file_create_error(normalized_path, caught_exc)

    # 7. Return the normalized, guaranteed-to-exist file
    return normalized_path


_DESIGN_NOTES = """
# ensure_file — "This File Exists Now"

## Purpose
The file counterpart of `ensure_dir`: returns a path that is certainly a
file, creating an empty one (and the folders above it) when allowed.

---

## 1. Moved From `validators/`, Same Two Corrections as `ensure_dir`
`except OSError` instead of the redundant tuple, and the "a directory took
the name between the check and `touch`" race is reported as a `StateError`
(step 6.1).

## 2. Existing Content Is Never Touched
`touch(exist_ok=True)` only runs for a path that did not exist. An existing
file is returned as it is — no truncation, no timestamp change.

## 3. `create=False` — A Pure Assertion
With creation off the function becomes "this file must already be there":
it returns the path, or raises `NotFoundError`. That makes it usable as a
precondition step in front of a read.

## 4. A File in the Parent Chain
`ensure_file("a_file/new.txt")` fails inside `ensure_dir` with a
`StateError` naming the blocking file — the real cause, not a vague
creation failure.
"""
