import os
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import to_path

@validate_call
def is_path_readable(
    path: PathLike,
    *,
    _validate_call: bool = True,
) -> bool:
    """Check whether a file can be read, or a directory listed, without raising.

    Args:
        path: The file or directory to check.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True for an existing regular file that can be opened for reading, or
        an existing directory whose entries can be listed; False otherwise
        (including a missing path, a broken symlink, or a special file).
    """

    # 1. Anything that cannot be turned into a path is not readable
    candidate = to_path(path)
    if candidate is None:
        return False

    # 2. Actually try — the only check that matches what a later read experiences
    try:

        # 2.1 A directory is readable when its entries can be listed
        if candidate.is_dir():
            with os.scandir(candidate):
                return True

        # 2.2 A file is readable when it can be opened for reading
        if candidate.is_file():
            with candidate.open("rb"):
                return True

    # 3. Permission and OS-level failures mean "not readable"
    except (OSError, ValueError):
        return False

    # 4. Missing paths, broken symlinks and special files
    return False


_DESIGN_NOTES = """
# is_path_readable — Can This Be Read Right Now?

## Purpose
The predicate behind the `IsPathReadable` rule and a natural precondition
for any extraction step ("is the source even readable?").

## Why Open It Instead of `os.access`
On Windows `os.access(path, R_OK)` ignores ACLs, and on every platform it
cannot see a file locked by another process. Opening the file (or listing
the directory) is the only check that agrees with what the next real read
will experience. Opening for reading changes nothing on disk.

## Regular Files and Directories Only
FIFOs, sockets and devices can block or have side effects when opened, so
they answer `False` without being touched.

## Never Raises for Disk Problems
Anything the OS refuses is a legitimate `False`. A wrong *type* of argument
is still rejected by the `PathLike` annotation before the body runs.
"""
