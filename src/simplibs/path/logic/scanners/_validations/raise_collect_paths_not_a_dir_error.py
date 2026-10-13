from pathlib import Path
from typing import NoReturn
from simplibs.exception import StateError


def raise_collect_paths_not_a_dir_error(path: Path) -> NoReturn:
    """Raise StateError when a scan root is an existing file instead of a directory."""

    # 1. Raise structured StateError wrapping a NotADirectoryError exception
    raise StateError(
        error_name="COLLECT_PATHS_NOT_A_DIRECTORY",
        label=f"root directory '{path}'",
        value=str(path),
        problem=(
            f"Cannot collect paths from '{path}'.",
            "Expected a root directory, but an existing regular file was found at this location.",
        ),
        expected="A path pointing to an existing directory that can be scanned.",
        how_to_fix=(
            "Provide a path to a directory instead of a regular file.",
            f"Check if '{path}' was mistakenly passed instead of its parent directory.",
        ),
        exception=NotADirectoryError,
    )


_DESIGN_NOTES = """
# raise_collect_paths_not_a_dir_error — Scan Root Is Not a Directory

## Purpose
Counterpart of `raise_collect_paths_not_found_error`: the root exists, but
is a file. Renamed from `raise_ensure_collect_paths_not_a_dir_error`; the
card itself is unchanged.
"""
