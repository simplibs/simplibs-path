import math
from collections.abc import Callable, Collection, Iterator
from pathlib import Path
# Outers
from ....annotations import PathLike
from .._validations import raise_nothing_to_collect_error
# Inners
from .as_path_predicate import as_path_predicate
from .build_ignore_matcher import build_ignore_matcher
from .generate_paths import generate_paths
from .resolve_scan_root import resolve_scan_root


def scan_paths(
    root_dir: PathLike,
    *,
    recursive: bool | int,
    include_filter: Callable[[Path], bool] | None,
    exclude_filter: Callable[[Path], bool] | None,
    ignore_names: Collection[str] | None,
    collect_files: bool,
    collect_dirs: bool,
) -> Iterator[Path]:
    """Prepare a scan and return the lazy iterator over its results.

    All checks and preparation happen now, when this is called; only the walk
    itself is deferred to iteration. Shared by every public scanner.

    Args:
        root_dir: The directory to scan.
        recursive: `True` for unlimited depth, `False` for the root's own
            entries only, or a non-negative `int` for a maximum depth.
        include_filter: Only paths it accepts are kept.
        exclude_filter: Paths it accepts are skipped.
        ignore_names: Entry names or glob patterns to skip entirely.
        collect_files: Whether files are collected.
        collect_dirs: Whether directories are collected.

    Returns:
        An iterator over the matching `Path`s (unsorted).

    Raises:
        ParamError: If both collect flags are False, or `ignore_names` is a string.
        NotFoundError: If the root does not exist.
        StateError: If the root is not a directory.
        AccessError: If the root cannot be listed.
    """

    # 1. Both flags off is a caller mistake, not an empty result
    if not collect_files and not collect_dirs:
        raise_nothing_to_collect_error()

    # 2. Validate and normalize the root now, not at the first iteration
    root = resolve_scan_root(root_dir)

    # 3. Prepare depth, ignore matcher and filters once, outside the loop
    max_depth = math.inf if recursive is True else int(recursive)
    is_ignored = build_ignore_matcher(ignore_names)
    include = None if include_filter is None else as_path_predicate(include_filter)
    exclude = None if exclude_filter is None else as_path_predicate(exclude_filter)

    # 4. Hand back the lazy generator
    return generate_paths(
        root,
        max_depth=max_depth,
        is_ignored=is_ignored,
        include=include,
        exclude=exclude,
        collect_files=collect_files,
        collect_dirs=collect_dirs,
    )


_DESIGN_NOTES = """
# scan_paths — Prepare Eagerly, Walk Lazily

## Purpose
Every public scanner differs only in its flags and what it does with the
result (return lazily, sort, ...). The preparation is identical, so it lives
here once, and each public function validates its own parameters
(`@validate_call`) and calls this.

## Why Not `collect_paths` Calling `iter_paths`
A chain of public functions would validate the same arguments two or three
times. Calling one internal, unvalidated function validates each public call
exactly once.

## `recursive` Semantics
`True` is unlimited, `False` is 0 (only the root's entries), an `int` is the
maximum depth below the root. `recursive is True` is an identity check on
purpose: `1 == True`, so equality would turn depth 1 into "unlimited".
"""
