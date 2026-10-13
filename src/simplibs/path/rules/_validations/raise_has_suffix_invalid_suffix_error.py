from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_has_suffix_invalid_suffix_error(suffix: Any) -> NoReturn:
    """Raise ParamError when a HasSuffix suffix has an invalid shape."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="HAS_SUFFIX_INVALID_SUFFIX_ERROR",
        label="HasSuffix.suffixes",
        value=suffix,
        problem=(
            f"{suffix!r} is not a valid file suffix.",
            "A suffix must be an empty string (no suffix) or a string such as '.txt', "
            "without any path separator.",
        ),
        expected="Strings such as '.py', '.tar.gz', or '' for a name without a suffix.",
        how_to_fix=(
            "Start each suffix with a dot, e.g. '.py' instead of 'py'.",
            "Remove path separators from the suffix.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_has_suffix_invalid_suffix_error — Suffix Shape Guard

## Purpose
The most common mistake is `HasSuffix("py")` — no dot, so it would match
names merely *ending* in "py". Rejecting the shape up front prevents a rule
that silently selects the wrong files. The shape rule is the library-wide
`is_valid_suffix`, shared with `change_suffix`.
"""
