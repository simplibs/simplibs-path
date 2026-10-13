from pathlib import Path
from typing import NoReturn
from simplibs.exception import StateError


def raise_ensure_dir_not_a_dir_error(path: Path) -> NoReturn:
    """Raise StateError when a path exists but is a file instead of a directory."""

    # 1. Raise structured StateError wrapping a NotADirectoryError exception
    raise StateError(
        error_name="PATH_IS_NOT_A_DIRECTORY",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Expected directory at '{path}', but an existing file was found at this location.",
        ),
        expected="A directory path or a non-existent path where a directory can be created.",
        how_to_fix=(
            "Provide a path to a directory or a location that does not yet exist.",
            f"Remove or rename the existing file at '{path}' if it should be replaced by a directory.",
        ),
        exception=NotADirectoryError,
    )


_DESIGN_NOTES = """
# raise_ensure_dir_not_a_dir_error — Directory Type Validation Helper

## Purpose
Provides a structured exception when `ensure_dir` encounters an existing filesystem item
at the given target path that is a file rather than a directory.

## Integration
- **Caller**: `ensure_dir` in `simplibs/path/base/ensure_dir.py`.
- Emits a structured `StateError` wrapping a `NotADirectoryError`.
"""