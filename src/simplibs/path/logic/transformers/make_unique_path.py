import os
from pathlib import Path
from simplibs.types import int_positive
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import split_name
from ._validations import raise_unique_path_exhausted_error
from .normalize_entry_path import normalize_entry_path


@validate_call
def make_unique_path(
    path: PathLike,
    *,
    max_attempts: int_positive = 1000,
) -> Path:
    """Return `path` itself if it is free, otherwise a numbered variant that is.

    `report.txt` becomes `report (1).txt`, `report (2).txt`, ... — the first
    name that does not exist yet. Nothing is created.

    Args:
        path: The wanted path.
        max_attempts: How many numbered variants to try before giving up.

    Returns:
        An absolute `Path` that did not exist at the moment of the call. Its
        directory is resolved (symlinks followed); the final name is kept as
        written, so a symlink there is never followed.

    Raises:
        ParamError: If `path` has no final name (a filesystem root).
        OperationError: If every variant up to `max_attempts` is taken.
        AccessError: If the path cannot be normalized.
    """

    # 1. Normalize the wanted path as an entry (directory resolved, name kept)
    normalized = normalize_entry_path(path)

    # 2. The wanted path is free — keep it as it is
    if not os.path.lexists(normalized):
        return normalized

    # 3. Try "name (1).ext", "name (2).ext", ... until one is free
    stem, suffix = split_name(normalized)
    for number in range(1, max_attempts + 1):
        candidate = normalized.with_name(f"{stem} ({number}){suffix}")
        if not os.path.lexists(candidate):
            return candidate

    # 4. Every candidate within the limit is taken
    raise_unique_path_exhausted_error(normalized, max_attempts)


_DESIGN_NOTES = """
# make_unique_path — Collision-Free Output Names

## Purpose
Lets a pipeline write a result next to others without overwriting them,
choosing the name the way file managers do ("report (1).txt").

---

## 1. `os.path.lexists`, Not `Path.exists`
`exists()` follows symlinks, so a *broken* symlink reports "does not
exist" — and writing to that name would write through the link to its
missing target. `lexists` treats the link itself as occupying the name.

## 2. Only the Directory Is Resolved
Delegated to `normalize_entry_path`: the final name is judged as written, so a
dangling link `out.txt -> nowhere` occupies the name `out.txt`.

## 3. Not Atomic — By Nature
The name is free at the moment of the call, not reserved. To claim a name for
certain, open the returned path with mode `"x"`; this function only chooses a
good candidate.

## 4. A Hard Attempt Limit
`max_attempts` stops the search on a directory where thousands of variants
exist. Reaching it is an operation failure (`OperationError`), not silent
success with a wrong name.

## 5. Compound Suffixes
`split_name` keeps `.tar.gz` together, so `archive.tar.gz` becomes
`archive (1).tar.gz` instead of `archive.tar (1).gz`.
"""
