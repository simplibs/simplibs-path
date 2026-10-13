from .PathLike import PathLike
from .PathPredicate import PathPredicate
from .RecursionDepth import RecursionDepth


_DESIGN_NOTES = """
# Path Shared Types Sub-Package

## Purpose
Annotations shared by several sub-packages (`transformers`, `ensure`,
`scanners`, `rules`, `actions`). Kept at package level instead of inside
`scanners/` because rules and functions outside the scanners need them too.

## Internal Components Registry

| Component        | Type       | Description                                                          |
| :--------------- | :--------- | :------------------------------------------------------------------- |
| `PathLike`       | Annotation | A non-blank string or a `Path` — the accepted shape of a path input. |
| `PathPredicate`  | Annotation | A `(Path) -> bool` callable; every `Rule` fits.                      |
| `RecursionDepth` | Annotation | `True`/`False` or a non-negative `int` — how deep a scan may go.     |
"""
