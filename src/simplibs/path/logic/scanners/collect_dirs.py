from collections.abc import Collection
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike, PathPredicate, RecursionDepth
# Inners
from ._helpers import scan_paths
from .ignore_names import DEFAULT_IGNORE_NAMES


@validate_call
def collect_dirs(
    root_dir: PathLike,
    *,
    recursive: RecursionDepth = True,
    include_filter: PathPredicate | None = None,
    exclude_filter: PathPredicate | None = None,
    ignore_names: Collection[str] | None = DEFAULT_IGNORE_NAMES,
) -> list[Path]:
    """Collect only the directories of a directory tree into a sorted list.

    The same as `collect_paths(..., collect_files=False, collect_dirs=True)`,
    with the type flags fixed. See `collect_paths` for the meaning of every
    parameter, the sorting and the raised errors.

    Args:
        root_dir: The root directory to scan (the root itself is not included).
        recursive: `True` for unlimited depth, `False` for the root's own
            entries only, or an `int` for a maximum depth.
        include_filter: A `Rule` or `(Path) -> bool` callable a directory must satisfy.
        exclude_filter: A `Rule` or `(Path) -> bool` callable that skips a directory.
        ignore_names: Entry names or glob patterns to skip entirely.

    Returns:
        The matching absolute directory `Path`s, sorted.
    """

    # 1. Run the shared scan with the type flags fixed, then sort
    return sorted(
        scan_paths(
            root_dir,
            recursive=recursive,
            include_filter=include_filter,
            exclude_filter=exclude_filter,
            ignore_names=ignore_names,
            collect_files=False,
            collect_dirs=True,
        )
    )


_DESIGN_NOTES = """
# collect_dirs — Directories Only

## Purpose
The directory counterpart of `collect_files` — for "which folders exist
under here" steps (mirroring a structure, picking project roots).

## The Root Is Not Included
Like every scanner, it lists what is *inside* `root_dir`. A caller who wants
the root as well adds it explicitly.
"""
