from simplibs.validate import validate_call
# Inners
from ._helpers import find_filename_problem


@validate_call
def is_valid_filename(
    name: str,
    *,
    portable: bool = True,
    _validate_call: bool = True,
) -> bool:
    """Check whether a string is a usable single file or directory name.

    Args:
        name: The candidate name — a name only, not a path.
        portable: If True (default), the name must be valid on both Windows
            and POSIX systems. If False, only the current OS's rules apply.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True if the name has no problem (see `find_filename_problem` for the
        exact rules); False otherwise.
    """

    # 1. A name is valid exactly when no problem is found
    return find_filename_problem(name, portable=portable) is None


_DESIGN_NOTES = """
# is_valid_filename — Is This String Safe as a File Name?

## Purpose
For code that builds file names from content (titles, identifiers, user
input) and must not produce a name the filesystem refuses or silently alters.

## Thin on Purpose
All rules live in `find_filename_problem`, which also explains *why* a name
fails — the `IsValidFilename` rule shows that text in its failure card. This
function only turns "no problem" into `True`.

## A Name, Not a Path
`"dir/file.txt"` is not a valid *name* (it contains a separator). Check
a path's last part with `Path(...).name` first, or use the rule, which does
that for `Path` values.
"""
