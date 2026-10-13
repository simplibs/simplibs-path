import os
from collections.abc import Callable, Collection
from fnmatch import fnmatchcase
# Inners
from .._validations import raise_ignore_names_not_names_error


_GLOB_CHARS = "*?["


def _ignore_nothing(name: str) -> bool:
    """The matcher used when no names are ignored."""
    return False


def build_ignore_matcher(
    ignore_names: Collection[str] | None,
) -> Callable[[str], bool]:
    """Build a fast `is_ignored(name)` function from a collection of names and patterns.

    Args:
        ignore_names: Entry names to skip. A name containing `*`, `?` or `[`
            is a glob pattern (`*.egg-info`); every other name matches
            exactly. `None` or an empty collection ignores nothing.

    Returns:
        A function answering True for a name that must be skipped. Matching
        follows the platform's case rules (case-insensitive on Windows).

    Raises:
        ParamError: If `ignore_names` is a single string — it would be
            split into characters.
    """

    # 1. A bare string is iterable — reject it before it becomes a set of characters
    if isinstance(ignore_names, str):
        raise_ignore_names_not_names_error(ignore_names)

    # 2. Nothing to ignore
    if not ignore_names:
        return _ignore_nothing

    # 3. Split exact names from glob patterns, case-normalized for the platform
    exact: set[str] = set()
    patterns: list[str] = []
    for name in ignore_names:
        key = os.path.normcase(name)
        if any(char in name for char in _GLOB_CHARS):
            patterns.append(key)
        else:
            exact.add(key)

    # 4. Exact names only — a single set lookup per entry
    if not patterns:
        return lambda name: os.path.normcase(name) in exact

    # 5. Exact names first, patterns only for names that did not match
    def is_ignored(name: str) -> bool:
        key = os.path.normcase(name)
        if key in exact:
            return True
        return any(fnmatchcase(key, pattern) for pattern in patterns)

    return is_ignored


_DESIGN_NOTES = """
# build_ignore_matcher — Names and Patterns, Compiled Once

## Purpose
The walker asks "is this name ignored?" for every entry. This function
prepares the answer once: a set for exact names (one hash lookup) and a
short list for glob patterns, consulted only when the set did not match.

## Why `normcase` + `fnmatchcase`
`os.path.normcase` makes names lower-case on Windows and leaves them alone
elsewhere, and `fnmatchcase` then compares *without* a second, implicit
normalization — one consistent platform rule for exact names and patterns.

## The Single-String Guard Lives Here
It is the one place every scanner passes `ignore_names` through, so the
`str` trap is caught once, with the dedicated error card, and cannot be
forgotten by a new scanner.

## Returns a Function, Not a Class
A closure over two local containers is the lightest thing that holds
prepared state, and it is trivial to replace in a test.
"""
