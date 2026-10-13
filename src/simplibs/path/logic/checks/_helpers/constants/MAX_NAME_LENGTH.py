from typing import Final


MAX_NAME_LENGTH: Final[int] = 255
"""Longest single file or directory name that common filesystems accept.

255 bytes on ext4/APFS-style filesystems, 255 UTF-16 code units on NTFS.
"""


_DESIGN_NOTES = """
# MAX_NAME_LENGTH — the 255 Limit

## Purpose
One named number for `find_length_problem`, instead of a bare 255 in the
code. It limits a single *name*, not a whole path (a full Windows path has a
separate, much larger limit that is not checked here).
"""
