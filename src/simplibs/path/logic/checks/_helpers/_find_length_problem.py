# Inners
from .constants import MAX_NAME_LENGTH


def _find_length_problem(
    name: str,
    *,
    windows: bool,
    posix: bool,
) -> str | None:
    """Return why a name is too long, or None if its length is acceptable.

    Args:
        name: A single file or directory name (no path).
        windows: Apply the NTFS limit (255 UTF-16 code units).
        posix: Apply the limit of most POSIX filesystems (255 bytes in UTF-8).

    Returns:
        A short description of the problem, or `None`.
    """

    # 1. POSIX filesystems count bytes — multi-byte characters use more of the limit
    if posix and len(name.encode("utf-8", "surrogatepass")) > MAX_NAME_LENGTH:
        return f"is longer than {MAX_NAME_LENGTH} bytes in UTF-8"

    # 2. NTFS counts UTF-16 code units — two bytes each
    if windows and len(name.encode("utf-16-le", "surrogatepass")) // 2 > MAX_NAME_LENGTH:
        return f"is longer than {MAX_NAME_LENGTH} UTF-16 characters"

    # 3. Within the limit
    return None


_DESIGN_NOTES = """
# find_length_problem — Name Length on Both Platform Families

## Purpose
The two limits are different units of the same number: bytes on POSIX,
UTF-16 units on Windows. A name of 128 `é` characters is 256 bytes (too long
on ext4) but only 128 units (fine on NTFS), so each platform family gets its
own count and a *portable* check applies both.

## `surrogatepass`
POSIX names may contain undecodable bytes that Python represents as lone
surrogates. Encoding them strictly would raise; `surrogatepass` encodes
them anyway, so a weird-but-existing name is measured, not rejected by
accident.
"""
