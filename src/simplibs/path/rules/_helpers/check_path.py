from collections.abc import Callable
from pathlib import Path
from typing import Any
# Outers
from ...logic.checks._helpers import to_path


def check_path(
    value: Any,
    check: Callable[[Path], bool],
) -> bool:
    """Run a filesystem check on a value, answering False instead of raising.

    Args:
        value: Any value; only a usable `str`/`Path` is checked.
        check: A callable taking the `Path` — e.g. `Path.is_file`.

    Returns:
        The strict `bool` answer of `check`, or `False` if `value` is not a
        usable path or the operating system refuses to answer.
    """

    # 1. Anything that cannot be turned into a path fails the rule
    path = to_path(value)
    if path is None:
        return False

    # 2. Ask the filesystem; a refusal (permissions, bad name) is a "no"
    try:
        return bool(check(path))
    except (OSError, ValueError):
        return False


_DESIGN_NOTES = """
# check_path — The Never-Raising Wrapper Every Filesystem Rule Needs

## Purpose
`Rule.is_valid` must return a strict `bool` and never raise. The pathlib
predicates mostly honor that for "no such file", but not for everything:
`Path.is_file()` re-raises `PermissionError` for a path behind a folder you
may not enter. One wrapper turns every such case into `False`, so no rule
has to remember the `try`.

## Strict `bool`
`bool(check(path))` — the contract tests compare with `is True`/`is False`,
so a truthy non-bool (an `int` from a custom check) is normalized here.
"""
