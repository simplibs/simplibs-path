from pathlib import Path
from typing import NoReturn
from simplibs.exception import AccessError


def raise_ensure_dir_error(
    path: Path,
    caught_exc: Exception,
) -> NoReturn:
    """Raise AccessError when directory creation fails due to OS or permission errors."""

    # 1. Raise structured AccessError wrapping the caught OS exception
    raise AccessError(
        error_name="DIRECTORY_CREATION_FAILED",
        label=f"directory '{path}'",
        value=str(path),
        problem=(
            f"Failed to guarantee directory at '{path}'.",
            f"OS reported: {caught_exc}",
        ),
        expected="A writable parent filesystem location where directory can be created.",
        how_to_fix=(
            f"Check write permissions for parent directory '{path.parent}'.",
            "Verify that the storage device is mounted and has sufficient free space.",
        ),
        exception=type(caught_exc),
    )


_DESIGN_NOTES = """
# raise_ensure_dir_error — Directory Creation Validation Helper

## Purpose
Provides a structured exception when `ensure_dir` encounters an OS-level or
permission error while attempting to create a directory tree using `mkdir`.

## Integration
- **Caller**: `ensure_dir` in `simplibs/path/base/ensure_dir.py`.
- Emits a structured `AccessError` wrapping the caught exception instance.
"""