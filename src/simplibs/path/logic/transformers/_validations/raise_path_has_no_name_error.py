from pathlib import Path
from typing import NoReturn
from simplibs.exception import ParamError


def raise_path_has_no_name_error(path: Path) -> NoReturn:
    """Raise ParamError when a path has no final name component to work with."""

    # 1. Raise structured ParamError wrapping a ValueError (what pathlib raises too)
    raise ParamError(
        error_name="PATH_HAS_NO_NAME",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Path '{path}' has no final name component.",
            "It is empty, the current directory ('.'), '..', or a filesystem root.",
        ),
        expected="A path ending with a file or directory name, e.g. 'dir/report.txt'.",
        how_to_fix=(
            "Provide a path that ends with a file or directory name.",
            "Normalize the path with `normalize_path` first if it is '.' or '..'.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_path_has_no_name_error — Nameless Path Diagnostic

## Purpose
`change_suffix` and `make_unique_path` both work on a path's final name. A
filesystem root (`/`, `C:\\`), `.` and `..` have no usable name:
`Path("/").with_suffix(".x")` raises a terse pathlib error, and
`Path("..").with_suffix(".x")` does not raise at all but produces the
nonsense name `...x`. One consistent card covers both cases.
"""
