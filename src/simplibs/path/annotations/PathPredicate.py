from pathlib import Path
from typing import Callable


PathPredicate = Callable[[Path], bool]
"""A `(Path) -> bool` predicate: a plain function, a lambda, or any `Rule`.

A `Rule` instance is callable (`Rule.__call__` delegates to `is_valid`), so
rules such as `HasSuffix(".py") & ~IsHidden()` fit this type directly —
no special protocol is needed.
"""


_DESIGN_NOTES = """
# PathPredicate — what a path filter may be

## Purpose
The annotation of `include_filter`, `exclude_filter` and `filter_paths`'s
`rule`: anything callable with one `Path` that returns a truthy/falsy answer.

---

## 1. Why the Former `HasIsValid` Protocol Is Gone

An earlier version also accepted any object with an `is_valid` method via a
structural `Protocol`. But every `Rule` is already callable, and
`build_typing_rule` turns `Callable[[...], R]` into a plain `IsCallable()`
check (argument and return types are never inspected). The protocol added a
second code path (`getattr(rule, "is_valid", rule)`) for objects that are
not callable but carry `is_valid` — a shape nobody produces. Removing it
leaves one rule: "it is callable".

## 2. Resolved Once, Outside the Loop

Consumers (`collect_paths`, `filter_paths`) resolve the predicate a single
time via `as_path_predicate` (see `scanners/_helpers/`), which unwraps a
`Rule` to its bound `is_valid` — skipping the one extra Python call of
`Rule.__call__` per entry.
"""
