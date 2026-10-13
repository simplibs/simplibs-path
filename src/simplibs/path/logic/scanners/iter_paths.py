from collections.abc import Collection, Iterator
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike, PathPredicate, RecursionDepth
# Inners
from ._helpers import scan_paths
from .ignore_names import DEFAULT_IGNORE_NAMES


@validate_call
def iter_paths(
    root_dir: PathLike,
    *,
    recursive: RecursionDepth = True,
    include_filter: PathPredicate | None = None,
    exclude_filter: PathPredicate | None = None,
    ignore_names: Collection[str] | None = DEFAULT_IGNORE_NAMES,
    collect_files: bool = True,
    collect_dirs: bool = False,
) -> Iterator[Path]:
    """Lazily yield the paths of a directory tree, one at a time.

    The memory-friendly sibling of `collect_paths`: nothing is held back, so
    a huge tree can be processed as it is discovered, and the walk can be
    stopped early. The results are NOT sorted and come in no promised order.

    Args:
        root_dir: The root directory to scan.
        recursive: `True` for unlimited depth, `False` for the root's own
            entries only, or an `int` for a maximum depth (0 = root's own
            entries, 1 = one level deeper, ...).
        include_filter: A `Rule` or `(Path) -> bool` callable. A path must
            satisfy it to be yielded.
        exclude_filter: A `Rule` or `(Path) -> bool` callable. A path that
            satisfies it is skipped (checked before `include_filter`).
            Excluding a directory does not hide what is inside it.
        ignore_names: Entry names (files and directories) or glob patterns
            (`*.egg-info`) to skip entirely — an ignored directory is not
            entered. Pass a collection, never a bare string; `None` ignores
            nothing.
        collect_files: Whether files are yielded.
        collect_dirs: Whether directories are yielded.

    Returns:
        A lazy iterator of absolute `Path`s. The root and the options are
        checked when `iter_paths` is called, not at the first `next()`.

    Raises:
        ParamError: If both collect flags are False, or `ignore_names` is a string.
        NotFoundError: If `root_dir` does not exist.
        StateError: If `root_dir` is not a directory.
        AccessError: If `root_dir` cannot be listed.
    """

    # 1. Prepare everything now; only the walk itself is lazy
    return scan_paths(
        root_dir,
        recursive=recursive,
        include_filter=include_filter,
        exclude_filter=exclude_filter,
        ignore_names=ignore_names,
        collect_files=collect_files,
        collect_dirs=collect_dirs,
    )


_DESIGN_NOTES = """
# iter_paths — the Lazy Scanner

## Purpose
`collect_paths` must finish the whole walk before returning anything.
For a large tree, or a pipeline that only needs the first match, that is
wasteful. `iter_paths` hands out paths as they are found.

## No Action Counterpart
An `Action` takes one value and returns one value; a generator is consumed
once and cannot be safely logged, validated or re-run by the action
machinery. Pipelines use `CollectPaths`/`CollectFiles`/`CollectDirs`, which
return a list.

## Eager Errors, Lazy Results
`iter_paths` is an ordinary function that returns a generator, not a
generator function itself. A generator function would run none of its body —
including the root checks — until the first `next()`, so a typo in the path
would surface in unrelated code, later.

## Order
Not sorted, not promised. Anything that needs a stable order uses
`collect_paths`.
"""
