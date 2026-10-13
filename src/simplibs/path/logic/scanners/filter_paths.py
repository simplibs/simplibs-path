from collections.abc import Collection
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathPredicate
# Inners
from ._helpers import as_path_predicate


@validate_call
def filter_paths(
    paths: Collection[Path],
    rule: PathPredicate,
) -> list[Path]:
    """Keep only the paths that satisfy a Rule or callable predicate.

    Args:
        paths: The paths to filter — a list, tuple or set (not a generator,
            which cannot be validated without being consumed; wrap it in
            `list(...)` first).
        rule: A `Rule` or `(Path) -> bool` callable. A path is kept when it
            returns a truthy value.

    Returns:
        A new list with the paths satisfying `rule`, in their original order.
    """

    # 1. Resolve the predicate once, outside the loop
    predicate = as_path_predicate(rule)

    # 2. Keep only the paths satisfying it
    return [path for path in paths if predicate(path)]


_DESIGN_NOTES = """
# filter_paths — Filter an Existing List of Paths

## Purpose
`collect_paths` filters while scanning. `filter_paths` filters a list you
already have — the result of an earlier step, or paths from elsewhere —
which is what `CollectFiles() >> FilterPaths(rule=...)` needs.

## What Changed
* **`rule` is required.** With `rule=None` the old version just copied the
  list — a no-op that, as an action, could only be a mistake.
* **`Collection[Path]` instead of `Iterable[Path]`.** `@validate_call`
  checks `Iterable[...]` by iterating it, which would silently exhaust a
  generator argument and then filter an empty list. A collection can be
  checked and still used.
* **`as_path_predicate`** replaces `getattr(rule, "is_valid", rule)`.
"""
