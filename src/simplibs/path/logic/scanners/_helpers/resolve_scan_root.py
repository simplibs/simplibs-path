import os
from pathlib import Path
# Outers
from ...transformers import normalize_path
# Inners
from .._validations import (
    raise_collect_paths_not_a_dir_error,
    raise_collect_paths_not_found_error,
    raise_collect_paths_root_unreadable_error,
)


def resolve_scan_root(root_dir: str | Path) -> Path:
    """Normalize a scan root and make sure it can actually be scanned.

    Args:
        root_dir: The directory the caller wants to scan.

    Returns:
        The normalized absolute directory `Path`.

    Raises:
        NotFoundError: If the root does not exist.
        StateError: If the root is not a directory.
        AccessError: If the root's entries cannot be listed.
    """

    # 1. Normalize the root
    normalized_root = normalize_path(root_dir)

    # 2. It must exist
    if not normalized_root.exists():
        raise_collect_paths_not_found_error(normalized_root)

    # 3. It must be a directory
    if not normalized_root.is_dir():
        raise_collect_paths_not_a_dir_error(normalized_root)

    # 4. It must be listable — otherwise the walk would silently return nothing
    try:
        with os.scandir(normalized_root):
            pass
    except OSError as caught_exc:
        raise_collect_paths_root_unreadable_error(normalized_root, caught_exc)

    # 5. Return the checked root
    return normalized_root


_DESIGN_NOTES = """
# resolve_scan_root — Fail Early, Before Any Walking

## Purpose
The root checks that used to sit inline in `collect_paths`, extracted so all
four scanners share them — and extended with the "unreadable" case.

## Why the Extra `scandir`
`walk_tree` skips what it cannot read. Without this probe, an unreadable root
would yield an empty list indistinguishable from an empty directory. One
`scandir` open on the root costs microseconds and turns a silent wrong answer
into an error.

## Eager by Design
It runs when the scanner is *called*. This matters for `iter_paths`: a bad
root must raise at the call, not at the first `next()` somewhere far away.
"""
