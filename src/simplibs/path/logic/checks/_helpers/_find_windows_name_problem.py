# Inners
from .constants import WINDOWS_FORBIDDEN_CHARS, WINDOWS_RESERVED_NAMES


def _find_windows_name_problem(name: str) -> str | None:
    """Return why a name is invalid on Windows, or None if it is fine there.

    Args:
        name: A single file or directory name (no path).

    Returns:
        A short description of the first problem found, or `None`.
    """

    # 1. A backslash is a path separator on Windows
    if "\\" in name:
        return "contains a path separator '\\'"

    # 2. Control characters and characters Windows forbids in names
    for char in name:
        if ord(char) < 32:
            return f"contains a control character (code {ord(char)})"
        if char in WINDOWS_FORBIDDEN_CHARS:
            return f"contains the character {char!r}, which Windows forbids in names"

    # 3. Windows silently strips a trailing dot or space
    if name.endswith((".", " ")):
        return "ends with a dot or a space, which Windows removes"

    # 4. Reserved device names — the part before the first dot decides
    base = name.split(".", 1)[0].rstrip(" ").upper()
    if base in WINDOWS_RESERVED_NAMES:
        return f"'{base}' is a reserved Windows device name"

    # 5. Nothing wrong
    return None


_DESIGN_NOTES = """
# find_windows_name_problem — Windows-Specific Name Rules

## Purpose
The Windows half of the filename check, separated from the platform-neutral
rules so `find_filename_problem` can apply it on Windows, or everywhere when
a *portable* name is wanted.

## Returns Text, Not a Bool
The same function feeds both `is_valid_filename` (needs a yes/no) and the
`IsValidFilename` rule's failure card (needs the reason). Returning the
reason once serves both and keeps a single source of truth.

## Order of Checks
Cheapest and most specific first; the reserved-name test comes last because
it needs the string split and upper-cased.
"""
