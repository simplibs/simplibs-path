from typing import Final


WINDOWS_FORBIDDEN_CHARS: Final[frozenset[str]] = frozenset('<>:"|?*')
"""Characters Windows does not allow inside a file name.

The path separators `/` and `\\` are handled separately (they are never
valid in a *name* on any platform / on Windows respectively), as are
control characters.
"""


_DESIGN_NOTES = """
# WINDOWS_FORBIDDEN_CHARS — Characters NTFS Rejects

## Purpose
The set `find_windows_name_problem` checks each character against. Kept
as its own constant, like the other name lists in this library, so it can
be read (and tested) at a glance.

## Why `:` Is Included
On Windows a colon in a name is not an error at the API level — it opens an
NTFS alternate data stream (`file.txt:hidden`). For a portable filename
check that is exactly the surprise to rule out.
"""
