from pathlib import Path
from typing import NamedTuple


class ScanEntry(NamedTuple):
    """One entry found by `walk_tree`: its path and what kind of entry it is.

    Attributes:
        path: The entry's full path (the scan root joined with its relative part).
        is_file: True for a regular file, or a symlink to one.
        is_dir: True for a directory, or a symlink to one.
    """

    path: Path
    is_file: bool
    is_dir: bool


_DESIGN_NOTES = """
# ScanEntry — an Entry Plus Its Kind, Learned Once

## Purpose
`os.scandir` hands over the entry type as a by-product of listing (free on
Windows, cached from the directory read on POSIX). Passing it along lets the
collectors decide "file or directory?" without asking the disk again — the
old code made two extra `stat` calls per entry.

## Never Neither
`walk_tree` yields only entries that are a file or a directory, so exactly
one of the two flags is True. Broken symlinks, FIFOs, sockets and devices
are not yielded at all.

## Why a `NamedTuple`
Tens of thousands are created per scan; a tuple subclass is as cheap as
Python offers, is immutable, and still reads like an object (`entry.path`).
"""
