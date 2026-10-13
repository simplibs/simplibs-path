from pathlib import Path
from typing import NoReturn
from simplibs.exception import AccessError


def raise_ensure_file_create_error(
    path: Path,
    caught_exc: Exception,
) -> NoReturn:
    """Raise AccessError when file creation fails due to OS or permission errors."""

    # 1. Raise structured AccessError wrapping the caught OS exception
    raise AccessError(
        error_name="FILE_CREATION_FAILED",
        label=f"file '{path}'",
        value=str(path),
        problem=(
            f"Failed to create file at '{path}'.",
            f"OS reported: {caught_exc}",
        ),
        expected="A writable directory location where a new file can be created.",
        how_to_fix=(
            f"Check write permissions for directory '{path.parent}'.",
            "Verify that the storage device is accessible and not read-only.",
        ),
        exception=type(caught_exc),
    )


_DESIGN_NOTES = """
# raise_ensure_file_create_error — File Creation Validation Helper

## Purpose
Provides a structured exception when `ensure_file` fails to touch or create a file on disk.

## Integration
- **Caller**: `ensure_file` in `simplibs/path/base/ensure_file.py`.
- Emits a structured `AccessError` wrapping the caught exception instance.
"""