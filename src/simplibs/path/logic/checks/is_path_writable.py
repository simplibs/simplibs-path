import os
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import can_create_inside, to_path


@validate_call
def is_path_writable(
    path: PathLike,
    *,
    _validate_call: bool = True,
) -> bool:
    """Check whether a path could be written to right now, without changing anything.

    Args:
        path: The path to check — an existing file, an existing directory,
            or a file that does not exist yet.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True if an existing file can be opened for appending, if a file can
        be created inside an existing directory, or if a missing file's
        parent directory exists and accepts new files. False otherwise —
        including a missing parent directory (nothing is created here).
    """

    # 1. Anything that cannot be turned into a path is not writable
    candidate = to_path(path)
    if candidate is None:
        return False

    # 2. Probe the real target — the only check that matches a later write
    try:

        # 2.1 An existing directory — can a file be created inside?
        if candidate.is_dir():
            return can_create_inside(candidate)

        # 2.2 An existing file — append mode never changes its content
        if candidate.is_file():
            with candidate.open("ab"):
                return True

        # 2.3 Something else already occupies the name (broken symlink, device)
        if os.path.lexists(candidate):
            return False

        # 2.4 A file that does not exist yet — its parent must accept new files
        parent = candidate.parent
        return parent.is_dir() and can_create_inside(parent)

    # 3. Permission and OS-level failures mean "not writable"
    except (OSError, ValueError):
        return False


_DESIGN_NOTES = """
# is_path_writable — Writable Without Side Effects

## Purpose
The predicate behind `IsPathWritable`: "if I write here next, will the OS
let me?".

---

## 1. Fixes Two Problems of the Old Version
The former version opened *any* path in append mode. For a path that did not
exist that **created an empty file** — a "check" with a lasting side effect,
contradicting its own docstring. It also reported `False` for every
directory. Now a missing file is judged by probing its parent directory
(`can_create_inside`, which leaves no trace), and a directory is writable
when files can be created inside it.

## 2. Existing Files: Append Mode
`open("ab")` fails on a read-only file, locked file or denied ACL, yet
neither truncates nor modifies anything.

## 3. Missing Parent Means False
Creating parent directories is `ensure_parent_dir`'s job. "Is it writable
*now*?" is honestly answered `False` when the folder is not there; a
pipeline that wants to create it first simply orders the steps that way.

## 4. Not a Reservation
The answer holds at the moment of the call. Another process can change
permissions or fill the disk before the actual write, so a real write must
still handle its own errors.
"""
