from pathlib import Path
from typing import NoReturn
from simplibs.exception import OperationError


def raise_unique_path_exhausted_error(
    path: Path,
    attempts: int,
) -> NoReturn:
    """Raise OperationError when no free numbered variant of a path was found."""

    # 1. Raise structured OperationError wrapping a FileExistsError
    raise OperationError(
        error_name="UNIQUE_PATH_EXHAUSTED",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Could not find a free name for '{path}' after {attempts} attempts.",
            "Every numbered candidate already exists.",
        ),
        expected="A path with at least one free numbered variant within the attempt limit.",
        how_to_fix=(
            "Clean up the existing numbered variants of this path.",
            "Use a different base name or target directory.",
            "Raise `max_attempts` if that many variants are really needed.",
        ),
        exception=FileExistsError,
    )


_DESIGN_NOTES = """
# raise_unique_path_exhausted_error — make_unique_path Diagnostic

## Purpose
`make_unique_path` tries "name (1).ext", "name (2).ext", ... up to
`max_attempts`. A hard limit is a safety net against an endless loop on a
pathological directory; reaching it is an operation failure, not a bad
argument, hence OperationError.
"""
