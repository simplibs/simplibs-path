from .filesystem import (
    IsDir,
    IsEmptyDir,
    IsEmptyFile,
    IsFile,
    IsPathReadable,
    IsPathWritable,
    IsSymlink,
    PathExists,
)
from .lexical import (
    AnyParentNameIs,
    HasSuffix,
    IsAbsolutePath,
    IsHidden,
    IsRelativePath,
    IsValidFilename,
    IsWithin,
    NameIs,
    ParentNameIs,
    StemIs,
)

__all__ = [
    # lexical — judge a path by its text
    "AnyParentNameIs",
    "HasSuffix",
    "IsAbsolutePath",
    "IsHidden",
    "IsRelativePath",
    "IsValidFilename",
    "IsWithin",
    "NameIs",
    "ParentNameIs",
    "StemIs",
    # filesystem — ask the disk
    "IsDir",
    "IsEmptyDir",
    "IsEmptyFile",
    "IsFile",
    "IsPathReadable",
    "IsPathWritable",
    "IsSymlink",
    "PathExists",
]


_DESIGN_NOTES = """
# Path Rules Sub-Package

## Purpose
`Rule` classes for paths: filters for scanners (`include_filter`,
`exclude_filter`, `filter_paths`), annotations for `@validate_call`
(`validated_type(Path, IsDir())`) and pipeline gates (`IsDir() >> CollectFiles()`).
Each is a thin wrapper over a function in `checks/` or a pathlib call.

## Two Groups
* `lexical/` — judge the path's *text*. Cheap; safe to run per entry.
* `filesystem/` — ask the disk. One or two syscalls per call.

## Composition
Combine them with the usual operators: `IsFile() & HasSuffix(".py") & ~IsHidden()`.
The description of that rule reads `existing file & suffix '.py' & not hidden path`.

## Domain Folder: `__all__`
As the other domain folders, this package defines `__all__` (the public
rules); the sub-packages and helpers are importable but not part of it.
"""
