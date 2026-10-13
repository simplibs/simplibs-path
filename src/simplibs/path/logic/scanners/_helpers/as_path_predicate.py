from collections.abc import Callable
from pathlib import Path
from simplibs.rules import Rule


def as_path_predicate(predicate: Callable[[Path], bool]) -> Callable[[Path], bool]:
    """Turn a Rule or a plain callable into the fastest `(Path) -> bool` call.

    Args:
        predicate: A `Rule` instance or any callable taking a `Path`.

    Returns:
        `predicate.is_valid` for a `Rule` (skipping the extra call of
        `Rule.__call__`), the callable itself otherwise.
    """

    # 1. A Rule — use its bound is_valid directly
    if isinstance(predicate, Rule):
        return predicate.is_valid

    # 2. Any other callable is used as it is
    return predicate


_DESIGN_NOTES = """
# as_path_predicate — Resolve a Filter Once

## Purpose
`collect_paths` and `filter_paths` call their filter once per entry, so the
choice "Rule or function?" is made a single time, before the loop. A `Rule`
is callable, but `Rule.__call__` only forwards to `is_valid` — calling
`is_valid` directly saves one Python call per entry.

## Replaces `getattr(rule, "is_valid", rule)`
The old duck-typing accepted any object that merely *had* an `is_valid`
attribute. An explicit `isinstance(..., Rule)` states what is meant, and the
`HasIsValid` protocol it served no longer exists.
"""
