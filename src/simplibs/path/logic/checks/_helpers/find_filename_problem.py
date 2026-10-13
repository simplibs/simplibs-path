import os
# Inners
from ._find_length_problem import _find_length_problem
from ._find_windows_name_problem import _find_windows_name_problem


def find_filename_problem(
    name: str,
    *,
    portable: bool = True,
) -> str | None:
    """Return why a string is not a usable file name, or None if it is.

    Args:
        name: A single file or directory name (no path).
        portable: If True (default), the name must be valid on both Windows
            and POSIX systems. If False, only the rules of the current
            operating system apply.

    Returns:
        A short description of the first problem found
        (`"contains the character '?', which Windows forbids in names"`),
        or `None` when the name is acceptable.
    """

    # 1. Rules that hold on every platform
    if not name.strip():
        return "is empty or blank"
    if name in (".", ".."):
        return f"'{name}' is a reserved directory reference"
    if "/" in name:
        return "contains a path separator '/'"
    if "\0" in name:
        return "contains a null byte"

    # 2. Decide which platform families apply
    is_windows = os.name == "nt"
    check_windows = portable or is_windows
    check_posix = portable or not is_windows

    # 3. Windows-specific rules
    if check_windows:
        problem = _find_windows_name_problem(name)
        if problem is not None:
            return problem

    # 4. Length, counted the way each applicable platform counts it
    return _find_length_problem(name, windows=check_windows, posix=check_posix)


_DESIGN_NOTES = """
# find_filename_problem — the One Source of Truth for Name Validity

## Purpose
Answers "is this string a usable file name?" with a reason, so both
`is_valid_filename` (bool) and the `IsValidFilename` rule's failure card
(text) are built on the same check.

---

## 1. Portable by Default
This library generates names from content (extraction output), so the
default is the strictest union of Windows and POSIX rules: a name that passes
works everywhere the result may later be copied. `portable=False` relaxes it
to the current OS only.

## 2. Blank Is a Problem on Every Platform
A name of spaces is legal on POSIX but unusable in practice and silently
altered on Windows; treating it as invalid everywhere is the useful answer.

## 3. What Is Not Checked
The *existence* of the name, the total path length (Windows' 260-character
`MAX_PATH`), and names that are valid but unwise (leading dashes, `~`). This
is a check of the string itself, not of the disk.
"""
