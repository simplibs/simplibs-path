from collections.abc import Callable, Iterator
from pathlib import Path
# Inners
from .walk_tree import walk_tree


def generate_paths(
    root: Path,
    *,
    max_depth: float | int,
    is_ignored: Callable[[str], bool],
    include: Callable[[Path], bool] | None,
    exclude: Callable[[Path], bool] | None,
    collect_files: bool,
    collect_dirs: bool,
) -> Iterator[Path]:
    """Lazily yield the paths of a tree that pass the type and filter checks.

    Args:
        root: The validated, normalized scan root.
        max_depth: See `walk_tree`.
        is_ignored: See `walk_tree`.
        include: If given, only paths it accepts are yielded.
        exclude: If given, paths it accepts are skipped (checked first).
        collect_files: Whether files are yielded.
        collect_dirs: Whether directories are yielded.

    Yields:
        Matching `Path`s, in walk order (unsorted).
    """

    # 1. Walk the tree
    for entry in walk_tree(root, max_depth=max_depth, is_ignored=is_ignored):

        # 1.1 Apply the file/directory type selection (a directory symlink counts as a directory)
        if entry.is_dir:
            if not collect_dirs:
                continue
        elif not collect_files:
            continue

        # 1.2 Apply the exclude filter — it wins over include
        if exclude is not None and exclude(entry.path):
            continue

        # 1.3 Apply the include filter
        if include is not None and not include(entry.path):
            continue

        # 1.4 Yield the matching path
        yield entry.path


_DESIGN_NOTES = """
# generate_paths — the Selection Loop, Written Once

## Purpose
The common core of `iter_paths` (yields it), `collect_paths` (sorts it) and
`collect_files`/`collect_dirs` (fix the flags): type selection, then
`exclude`, then `include`.

## Positive Type Selection
The old loop skipped "files when files are off" and "directories when
directories are off" separately, so an entry that was neither (a broken
symlink) slipped through *both* guards and was collected. `walk_tree` now
yields only files and directories, and the selection below handles both
cases explicitly.

## Filters Do Not Prune
`exclude` hides a directory *entry* but its contents are still walked and
judged on their own — only `ignore_names` prunes a subtree. This is
deliberate (a filter on a directory says nothing about its children) and
documented on the public functions.
"""
