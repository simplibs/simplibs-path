from pathlib import Path
from typing import Any
from simplibs.exception import ValidationError


def build_not_a_path_exception(
    *,
    error_name: str,
    expected: str,
    value: Any,
    value_name: str | None,
    context: str | None,
) -> Exception:
    """Build the failure card for a value that cannot even be treated as a path.

    Args:
        error_name: The calling rule's `error_name`.
        expected: The calling rule's `expected` sentence.
        value: The rejected value.
        value_name: The label passed to `build_exception`.
        context: The context passed to `build_exception`.

    Returns:
        A `ValidationError` — wrapping `TypeError` for a non-string, non-Path
        value, and `ValueError` for a blank string or one with a null byte.
    """

    # 1. A str/Path that is still unusable — blank or containing a null byte
    if isinstance(value, (str, Path)):
        problem = f"Value {value!r} cannot be used as a path (it is blank or contains a null byte)."
        how_to_fix = "Provide a non-blank path without null bytes."
        exception_type = ValueError

    # 2. Not a string or Path at all
    else:
        problem = f"Value {value!r} of type '{type(value).__name__}' is not a string or Path."
        how_to_fix = "Provide a path as a str or a Path object."
        exception_type = TypeError

    # 3. Build the exception
    return ValidationError(
        error_name=error_name,
        label=value_name,
        expected=expected,
        value=value,
        problem=problem,
        context=context,
        how_to_fix=how_to_fix,
        exception=exception_type,
    )


_DESIGN_NOTES = """
# build_not_a_path_exception — Wrong Kind of Value, Said Once

## Purpose
Every path rule has the same first failure branch: the value is not a path
at all. This builds that card for all of them, mirroring the `if not
isinstance(value, str)` branch of `Contains`/`IsString` — with the one extra
distinction a path needs: a *blank* string is a `str` and still not a path.

## Same `error_name` in Both Branches
A rule's card keeps one `error_name` whatever went wrong (as `Contains` uses
`CONTAINS_ERROR` for both its type and its value failure); only the
wrapped `exception` type (`TypeError` / `ValueError`) differs.
"""
