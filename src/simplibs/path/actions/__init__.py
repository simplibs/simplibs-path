from .ChangeSuffix import ChangeSuffix
from .CollectDirs import CollectDirs
from .CollectFiles import CollectFiles
from .CollectPaths import CollectPaths
from .EnsureDir import EnsureDir
from .EnsureFile import EnsureFile
from .EnsureParentDir import EnsureParentDir
from .FilterPaths import FilterPaths
from .MakeUniquePath import MakeUniquePath
from .NormalizeEntryPath import NormalizeEntryPath
from .NormalizePath import NormalizePath
from .RebasePath import RebasePath
from .RelativizePath import RelativizePath


__all__ = [
    # transformers — path in, path out
    "NormalizeEntryPath",
    "NormalizePath",
    "RebasePath",
    "RelativizePath",
    "ChangeSuffix",
    "MakeUniquePath",
    # ensure — make a filesystem state true
    "EnsureDir",
    "EnsureFile",
    "EnsureParentDir",
    # scanners — look at a tree
    "CollectPaths",
    "CollectFiles",
    "CollectDirs",
    "FilterPaths",
]


_DESIGN_NOTES = """
# Path Actions Sub-Package

## Purpose
Every function of the library that takes one main value and returns one
result, as an `Action`: constructed once with its options, then called with
the main input and chainable with `>>`, `&` and `|`.

```python
pipeline = (
    IsDir()                                   # a Rule — becomes a guard step
    >> CollectFiles(include_filter=HasSuffix(".py"))
    >> FilterPaths(rule=~IsHidden())
)
paths = pipeline("~/project")
````

## What Is Not Here

- **Predicates (`checks/`, rules):** a bool is not a pipeline value. A Rule\
  already works as a step — `Action` turns it into a pass-through `guard`.
- **`iter_paths`:** a generator is consumed once and cannot be logged or\
  re-run by the action machinery; pipelines use the list-returning collectors.

## Async

All thirteen are synchronous actions, so `await action.acall(data)` runs them\
in a worker thread — the right model for blocking file-system calls.

## Domain Folder: `__all__`

Like `rules/`, this package defines `__all__` (the public actions).\
"""