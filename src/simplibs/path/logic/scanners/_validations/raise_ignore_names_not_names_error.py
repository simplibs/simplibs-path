from typing import NoReturn
from simplibs.exception import ParamError


def raise_ignore_names_not_names_error(value: str) -> NoReturn:
    """Raise ParamError when `ignore_names` is a single string instead of a collection."""

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="IGNORE_NAMES_NOT_A_COLLECTION",
        label="ignore_names",
        value=value,
        problem=(
            f"A single string {value!r} was passed instead of a collection of names.",
            "A string is iterable, so it would be silently split into single characters.",
        ),
        expected="A collection of entry names, e.g. a tuple, list, set or frozenset of strings.",
        how_to_fix=(
            f"Wrap the name in a collection: ignore_names=({value!r},).",
            "Extend the defaults with a union: DEFAULT_IGNORE_NAMES | {'my_dir'}.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_ignore_names_not_names_error — The Single-String Trap

## Purpose
`str` is a `Collection[str]`, so the `@validate_call` annotation alone
cannot tell `ignore_names=".git"` from `ignore_names=(".git",)`. Without
this explicit check the first form would be read as the names
`{".", "g", "i", "t"}` — ignoring nothing useful and hiding every entry
named `g`, `i` or `t`. The scanners check for `str` in their body and
raise this card instead.
"""
