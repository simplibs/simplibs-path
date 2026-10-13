from collections.abc import Collection
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike, PathPredicate, RecursionDepth
# Inners
from ._helpers import scan_paths
from .ignore_names import DEFAULT_IGNORE_NAMES


@validate_call
def collect_files(
    root_dir: PathLike,
    *,
    recursive: RecursionDepth = True,
    include_filter: PathPredicate | None = None,
    exclude_filter: PathPredicate | None = None,
    ignore_names: Collection[str] | None = DEFAULT_IGNORE_NAMES,
) -> list[Path]:
    """Collect only the files of a directory tree into a sorted list.

    The same as `collect_paths(..., collect_files=True, collect_dirs=False)`,
    with the type flags fixed. See `collect_paths` for the meaning of every
    parameter, the sorting and the raised errors.

    Args:
        root_dir: The root directory to scan.
        recursive: `True` for unlimited depth, `False` for the root's own
            entries only, or an `int` for a maximum depth.
        include_filter: A `Rule` or `(Path) -> bool` callable a file must satisfy.
        exclude_filter: A `Rule` or `(Path) -> bool` callable that skips a file.
        ignore_names: Entry names or glob patterns to skip entirely.

    Returns:
        The matching absolute file `Path`s, sorted.
    """

    # 1. Run the shared scan with the type flags fixed, then sort
    return sorted(
        scan_paths(
            root_dir,
            recursive=recursive,
            include_filter=include_filter,
            exclude_filter=exclude_filter,
            ignore_names=ignore_names,
            collect_files=True,
            collect_dirs=False,
        )
    )


_DESIGN_NOTES = """
# collect_files — Files Only

## Why a Real Function, Not a `functools.partial`
The `CollectFiles` action used to be built from
`partial(collect_paths, collect_files=True, collect_dirs=False)`. A partial
only changes the *defaults* — the flags stayed in the signature, so
`CollectFiles(collect_dirs=True)` quietly broke the "locked" promise, and
`create_action` needs a `__name__` that a partial does not have.

A function with the flags removed from its signature cannot be mis-used,
has a truthful docstring, and wraps cleanly into an action.
"""
