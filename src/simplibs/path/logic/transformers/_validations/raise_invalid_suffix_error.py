from typing import NoReturn
from simplibs.exception import ParamError


def raise_invalid_suffix_error(suffix: str) -> NoReturn:
    """Raise ParamError when a new file suffix has an invalid shape."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="INVALID_PATH_SUFFIX",
        label="new_suffix",
        value=suffix,
        problem=(
            f"Suffix {suffix!r} is not a valid file suffix.",
            "A suffix must be empty, or start with a dot followed by at least one character, "
            "without any path separator.",
        ),
        expected="An empty string (removes the suffix) or a string such as '.txt'.",
        how_to_fix=(
            "Start the suffix with a dot, e.g. '.txt' instead of 'txt'.",
            "Remove path separators ('/' or '\\\\') from the suffix.",
            "Use an empty string if the suffix should be removed.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_invalid_suffix_error — change_suffix Argument Diagnostic

## Purpose
`Path.with_suffix` has its own errors, but they are terse and differ between
Python versions. Validating the suffix up front gives one consistent,
actionable card — and prevents a suffix such as '/etc' from silently
changing the directory part of the path.
"""
