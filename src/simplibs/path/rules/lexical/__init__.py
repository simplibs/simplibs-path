from .AnyParentNameIs import AnyParentNameIs
from .HasSuffix import HasSuffix
from .IsAbsolutePath import IsAbsolutePath
from .IsHidden import IsHidden
from .IsRelativePath import IsRelativePath
from .IsValidFilename import IsValidFilename
from .IsWithin import IsWithin
from .NameIs import NameIs
from .ParentNameIs import ParentNameIs
from .StemIs import StemIs


_DESIGN_NOTES = """
# Path Lexical Rules Sub-Package

## Purpose
Rules that judge a path by its *text* — no disk access (apart from the
optional symlink resolution of `IsWithin`). They are cheap enough to run per
entry in a filter over a whole tree.

## Internal Components Registry

| Component         | Type | Description                                                         |
| :---------------- | :--- | :------------------------------------------------------------------ |
| `AnyParentNameIs` | Rule | Some folder above the path has a name that satisfies another rule.  |
| `HasSuffix`       | Rule | The name ends with one of the given suffixes.                       |
| `IsAbsolutePath`  | Rule | The path is absolute.                                               |
| `IsHidden`        | Rule | The final name starts with a dot (optionally: Windows attribute).   |
| `IsRelativePath`  | Rule | The path is relative.                                               |
| `IsValidFilename` | Rule | A string/final name is usable as a file name.                       |
| `IsWithin`        | Rule | The path lies inside a root directory.                              |
| `NameIs`          | Rule | The final name satisfies another rule.                              |
| `ParentNameIs`    | Rule | The containing folder's name satisfies another rule.                |
| `StemIs`          | Rule | The name without its last suffix satisfies another rule.            |
"""
