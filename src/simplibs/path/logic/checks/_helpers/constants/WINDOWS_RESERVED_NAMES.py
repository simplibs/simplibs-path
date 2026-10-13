from typing import Final


WINDOWS_RESERVED_NAMES: Final[frozenset[str]] = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{number}" for number in range(10)}
    | {f"LPT{number}" for number in range(10)}
)
"""Device names Windows reserves, in upper case.

A file name is reserved when its part before the first dot, ignoring case
and trailing spaces, is one of these — `con`, `CON.txt` and `nul.log` all are.
"""


_DESIGN_NOTES = """
# WINDOWS_RESERVED_NAMES — Legacy DOS Device Names

## Purpose
`CON`, `PRN`, `AUX`, `NUL`, `COM0`–`COM9`, `LPT0`–`LPT9` still refer to
devices on Windows, whatever extension follows. Creating a file with such a
name fails or silently writes to the device — a classic portability trap
for tools that generate file names from content.

## Upper Case, Matched Case-Insensitively
The names are stored in upper case; the caller upper-cases the candidate.
"""
