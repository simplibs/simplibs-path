from pathlib import Path
from typing import NoReturn
from simplibs.exception import NotFoundError


def raise_collect_paths_not_found_error(path: Path) -> NoReturn:
    """Raise NotFoundError when a scan targets a non-existent root directory."""

    # 1. Raise structured NotFoundError wrapping a FileNotFoundError exception
    raise NotFoundError(
        error_name="COLLECT_PATHS_ROOT_NOT_FOUND",
        label=f"root directory '{path}'",
        value=str(path),
        problem=(
            f"Cannot scan directory tree at '{path}'.",
            "The specified root directory does not exist on disk.",
        ),
        expected="An existing directory path to use as the root for path collection.",
        how_to_fix=(
            f"Verify that the path '{path}' exists before collecting paths from it.",
            "Ensure parent directories are correctly spelled and accessible.",
        ),
        exception=FileNotFoundError,
    )


_DESIGN_NOTES = """
# raise_collect_paths_not_found_error — Missing Scan Root Diagnostic

## Purpose
Shared by every scanner that walks a tree (`collect_paths`, `collect_files`,
`collect_dirs`, `iter_paths`).

## Renamed From `raise_ensure_collect_paths_not_found_error`
Nothing is ensured here — the `ensure` prefix was a leftover. The how-to-fix
text no longer names `collect_paths` specifically, since four functions
share this card.
"""
