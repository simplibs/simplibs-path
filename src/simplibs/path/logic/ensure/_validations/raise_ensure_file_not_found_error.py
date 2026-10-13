from pathlib import Path
from typing import NoReturn
from simplibs.exception import NotFoundError


def raise_ensure_file_not_found_error(path: Path) -> NoReturn:
    """Raise NotFoundError when a required file is missing and create=False."""

    # 1. Raise structured NotFoundError wrapping a FileNotFoundError exception
    raise NotFoundError(
        error_name="FILE_NOT_FOUND",
        label=f"file '{path}'",
        value=str(path),
        problem=(
            f"Required file '{path}' does not exist on disk.",
            "Automatic creation was disabled because `create=False` was passed.",
        ),
        expected="An existing file path, or call ensure_file with create=True.",
        how_to_fix=(
            f"Ensure the file exists at '{path}' before invoking ensure_file.",
            "Set `create=True` if you want ensure_file to create missing files automatically.",
        ),
        exception=FileNotFoundError,
    )


_DESIGN_NOTES = """
# raise_ensure_file_not_found_error — File Absence Validation Helper

## Purpose
Provides a structured exception when `ensure_file` is called with `create=False` and the target file does not exist.

## Integration
- **Caller**: `ensure_file` in `simplibs/path/base/ensure_file.py`.
- Emits a structured `NotFoundError` wrapping a `FileNotFoundError`.
"""