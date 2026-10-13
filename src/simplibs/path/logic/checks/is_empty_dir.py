import os
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import to_path


@validate_call
def is_empty_dir(
    path: PathLike,
    *,
    _validate_call: bool = True,
) -> bool:
    """Check whether a path is an existing directory with no entries.

    Args:
        path: The path to check.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True only for an existing, listable, empty directory. False for a
        non-empty directory, a file, a missing path, or a directory that
        cannot be listed (its emptiness is unknown).
    """

    # 1. Anything that cannot be turned into a path is not an empty directory
    candidate = to_path(path)
    if candidate is None:
        return False

    # 2. Ask for the first entry only — never list the whole directory
    try:
        with os.scandir(candidate) as entries:
            return next(entries, None) is None

    # 3. Not a directory, missing, or not listable — not (known to be) empty
    except (OSError, ValueError):
        return False


_DESIGN_NOTES = """
# is_empty_dir — Cheap Emptiness Test

## Purpose
Used by the `IsEmptyDir` rule, and useful before cleanup or output steps
("only write into an empty folder").

## First Entry Only
`next(entries, None)` stops after one entry; a directory with a million
files costs the same as an empty one. `os.scandir` also never raises for
`.` and `..` — they are not yielded.

## Unknown Is False
A directory that cannot be listed (permissions) is neither known to be
empty nor known to be non-empty. The predicate answers `False` — "not
proven empty" — which is the safe side for a cleanup decision.
"""
