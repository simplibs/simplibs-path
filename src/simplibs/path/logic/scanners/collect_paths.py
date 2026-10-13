from collections.abc import Collection
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike, PathPredicate, RecursionDepth
# Inners
from ._helpers import scan_paths
from .ignore_names import DEFAULT_IGNORE_NAMES


@validate_call
def collect_paths(
    root_dir: PathLike,
    *,
    recursive: RecursionDepth = True,
    include_filter: PathPredicate | None = None,
    exclude_filter: PathPredicate | None = None,
    ignore_names: Collection[str] | None = DEFAULT_IGNORE_NAMES,
    collect_files: bool = True,
    collect_dirs: bool = False,
) -> list[Path]:
    """Scan a directory tree and collect the matching paths into a sorted list.

    Args:
        root_dir: The root directory to scan.
        recursive: `True` for unlimited depth, `False` for the root's own
            entries only, or an `int` for a maximum depth (0 = root's own
            entries, 1 = one level deeper, ...).
        include_filter: A `Rule` or `(Path) -> bool` callable. A path must
            satisfy it to be collected.
        exclude_filter: A `Rule` or `(Path) -> bool` callable. A path that
            satisfies it is skipped (checked before `include_filter`).
            Excluding a directory does not hide what is inside it — only
            `ignore_names` prunes a subtree.
        ignore_names: Entry names (files and directories) or glob patterns
            (`*.egg-info`) to skip entirely — an ignored directory is not
            entered. Defaults to `DEFAULT_IGNORE_NAMES`; extend it with
            `DEFAULT_IGNORE_NAMES | {"my_dir"}`. Pass a collection, never a
            bare string; `None` ignores nothing.
        collect_files: Whether files are collected (default True).
        collect_dirs: Whether directories are collected (default False).

    Returns:
        The matching absolute `Path`s, sorted by path parts (a directory's
        contents sort right after the directory itself). Symlinks to files
        and directories are collected as what they point to; broken
        symlinks and special files never are.

    Raises:
        ParamError: If both collect flags are False, or `ignore_names` is a string.
        NotFoundError: If `root_dir` does not exist.
        StateError: If `root_dir` is not a directory.
        AccessError: If `root_dir` cannot be listed.
    """

    # 1. Run the shared scan and sort what it finds
    return sorted(
        scan_paths(
            root_dir,
            recursive=recursive,
            include_filter=include_filter,
            exclude_filter=exclude_filter,
            ignore_names=ignore_names,
            collect_files=collect_files,
            collect_dirs=collect_dirs,
        )
    )


_DESIGN_NOTES = """
# collect_paths — the General Scanner

## Purpose
The list-returning scanner every extraction pipeline starts from, with both
type flags exposed. `collect_files` and `collect_dirs` are its fixed-flag
presets.

---

## 1. What Changed From the Previous Version
* **`ignore_dirs` → `ignore_names`**, applied to files too, with glob
  patterns, and a narrower default (no more silently hidden `build/`, `dist/`).
* **Broken symlinks and special files are no longer collected.** A positive
  type check replaces two negative ones that an entry of neither kind slipped
  through.
* **Both flags off raises** instead of returning `[]` before even checking
  the root.
* **An unreadable root raises** instead of looking like an empty tree.
* **One `scandir` per directory** instead of up to five `stat` calls per entry.
* **`Collection`, not `Iterable`, for `ignore_names`.** `@validate_call`
  checks `Iterable[...]` by iterating it — which would exhaust a generator
  argument before the function ever saw it.

## 2. Sorted by Path Parts
`Path` objects compare part by part, so `a/b.txt` sorts after the directory
`a` and before `a.txt`. That is tree order, and on Windows it is
case-insensitive, matching how Explorer lists a folder.

## 3. Absolute Paths
Entries are the normalized root joined with their relative part, so the
result needs no further `normalize_path`.
"""
