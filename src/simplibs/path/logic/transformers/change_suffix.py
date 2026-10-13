from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import is_valid_suffix

from ._validations import raise_invalid_suffix_error, raise_path_has_no_name_error


@validate_call
def change_suffix(
    path: PathLike,
    new_suffix: str,
) -> Path:
    """Replace the last suffix of a path (or add / remove one).

    Pure path arithmetic: nothing is read from or written to the disk and
    `~` is not expanded — combine with `normalize_path` if you need that.

    Args:
        path: The path whose suffix changes.
        new_suffix: The new suffix, including the dot (`".md"`), or an
            empty string to remove the current suffix.

    Returns:
        A new `Path`; only the last suffix is replaced, so
        `a.tar.gz` + `".zip"` becomes `a.tar.zip`.

    Raises:
        ParamError: If `new_suffix` is malformed, or `path` has no final
            name (a root, `.` or `..`).
    """

    # 1. Validate the shape of the new suffix
    if not is_valid_suffix(new_suffix):
        raise_invalid_suffix_error(new_suffix)

    # 2. The path needs a final name to carry a suffix
    result = Path(path)
    if result.name in ("", ".."):
        raise_path_has_no_name_error(result)

    # 3. Replace, add or remove the suffix
    return result.with_suffix(new_suffix)


_DESIGN_NOTES = """
# change_suffix — Suffix Replacement With Up-Front Validation

## Purpose
A thin, safe wrapper over `Path.with_suffix`, existing as its own function
(and `ChangeSuffix` action) so that "write the result next to the source,
but as .md" is one named step in a pipeline.

---

## 1. Why Validate Before Calling `with_suffix`
`with_suffix` has its own checks, but they are terse, differ slightly
between Python versions, and let `..` through (producing `...md`). Validating
first gives one consistent card and rules out a suffix such as `"/etc"`,
which could otherwise reach the directory part of a path.

## 2. The Shape Check Is Shared
`is_valid_suffix` (package `_helpers/`) defines what a suffix looks like;
the `HasSuffix` rule uses the very same function.

## 3. Backslash Is Rejected on Every Platform
It is a legal filename character on POSIX, but a path separator on Windows;
a suffix containing it cannot be portable, and portability is the point of
this library's filename handling.

## 4. Lexical on Purpose
No `expanduser`, no `resolve`, no disk access: a transformer that only
changes a name has no business touching the filesystem. In a pipeline,
`NormalizePath() >> ChangeSuffix(new_suffix=".md")` does both explicitly.
"""
