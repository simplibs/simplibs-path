import os
import stat


def is_link_like(entry: os.DirEntry) -> bool:
    """Check whether a directory entry is a symlink or a Windows junction.

    Args:
        entry: A directory entry from `os.scandir`.

    Returns:
        True for a symlink on any platform, and — on Windows — for a
        directory junction (mount point). Entering such a directory could
        loop forever or leave the scanned tree.
    """

    # 1. A symlink, on any platform
    if entry.is_symlink():
        return True

    # 2. Only Windows has junctions — nothing more to check elsewhere
    if os.name != "nt":
        return False

    # 3. A junction reports itself as a mount-point reparse tag (cached by scandir, no extra syscall)
    reparse_tag = getattr(entry.stat(follow_symlinks=False), "st_reparse_tag", 0)
    return reparse_tag == stat.IO_REPARSE_TAG_MOUNT_POINT


_DESIGN_NOTES = """
# is_link_like — Do Not Follow This Directory

## Purpose
`walk_tree` follows real directories only. Python's `is_symlink()` misses
Windows **junctions** (created by `mklink /J`, common for relocated user
folders): `is_dir()` is True, `is_symlink()` is False, and a junction
pointing at a parent directory makes a naive walk run until the path is too
long.

## Why the Reparse Tag, Not "Any Reparse Point"
Cloud-sync placeholders (OneDrive Files On-Demand) are reparse points too,
but ordinary folders in every other respect — treating all reparse points
as links would silently skip real content. Only the mount-point tag
identifies a junction.
"""
