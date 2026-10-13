from typing import NoReturn
from simplibs.exception import ParamError


def raise_has_suffix_no_suffixes_error() -> NoReturn:
    """Raise ParamError when HasSuffix is constructed without any suffix."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="HAS_SUFFIX_NO_SUFFIXES_ERROR",
        label="HasSuffix.suffixes",
        value=(),
        problem=(
            "HasSuffix() was created without any suffix.",
            "A rule without a suffix to look for could never accept or reject anything.",
        ),
        expected="At least one suffix, e.g. HasSuffix('.py') or HasSuffix('.md', '.rst').",
        how_to_fix=(
            "Pass one or more suffixes: HasSuffix('.py').",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_has_suffix_no_suffixes_error — Empty Rule Guard

## Purpose
Mirrors the "at least one rule" guard of `AllOf`/`AnyOf`: `HasSuffix()` with
nothing to look for is almost certainly a forgotten argument.
"""
