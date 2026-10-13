from pathlib import Path
from typing import NoReturn
from simplibs.exception import StateError


def raise_ensure_file_not_a_file_error(path: Path) -> NoReturn:
    """Raise StateError when a path exists but is a directory instead of a file."""

    # 1. Raise structured StateError wrapping an IsADirectoryError exception
    raise StateError(
        error_name="PATH_IS_NOT_A_FILE",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Expected file at '{path}', but an existing directory was found at this location.",
        ),
        expected="A regular file path or a non-existent path where a file can be created.",
        how_to_fix=(
            "Provide a path pointing to a file rather than a directory.",
            f"Remove or rename the existing directory at '{path}' if a file is intended.",
        ),
        exception=IsADirectoryError,
    )


_DESIGN_NOTES = """
# raise_ensure_file_not_a_file_error — File Type Validation Helper

## Purpose
Provides a structured exception when `ensure_file` encounters an existing directory
where a regular file was expected.

## Integration
- **Caller**: `ensure_file` in `simplibs/path/base/ensure_file.py`.
- Emits a structured `StateError` wrapping an `IsADirectoryError`.
"""