from pathlib import Path
from typing import NoReturn
from simplibs.exception import ParamError


def raise_path_not_within_root_error(
    path: Path,
    root: Path,
) -> NoReturn:
    """Raise ParamError when a path cannot be expressed relative to a root directory."""

    # 1. Raise structured ParamError wrapping a ValueError (what Path.relative_to raises)
    raise ParamError(
        error_name="PATH_NOT_WITHIN_ROOT",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Path '{path}' is not located inside the root directory '{root}'.",
            "The path cannot be expressed relative to this root.",
        ),
        expected=f"A path located inside '{root}'.",
        how_to_fix=(
            f"Provide a path that starts with '{root}'.",
            "Check that both paths are absolute, or both are relative to the same base.",
            "Normalize both paths with `normalize_path` before comparing them.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_path_not_within_root_error — Containment Failure Diagnostic

## Purpose
Shared by `rebase_path` (path vs. `source_root`) and `relativize_path`
(path vs. `root`): both need "this path lives under that root" and fail the
same way when it does not.

## Why ParamError With a ValueError
The caller supplied a combination of arguments that cannot work together —
a parameter problem. `ValueError` is what `Path.relative_to` itself raises,
so code that already catches it keeps working.
"""
