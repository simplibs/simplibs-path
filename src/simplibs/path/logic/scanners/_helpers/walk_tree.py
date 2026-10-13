import os
from collections.abc import Callable, Iterator
from pathlib import Path
# Inners
from .is_link_like import is_link_like
from .ScanEntry import ScanEntry


def walk_tree(
    root: Path,
    *,
    max_depth: float | int,
    is_ignored: Callable[[str], bool],
) -> Iterator[ScanEntry]:
    """Walk a directory tree, yielding every file and directory it contains.

    Args:
        root: The directory to walk (must already be validated and normalized).
        max_depth: The deepest directory level whose entries are listed
            (0 = only the entries of `root`; `math.inf` = unlimited).
        is_ignored: Called with each entry's name — a True answer skips the
            entry and, for a directory, everything below it.

    Yields:
        A `ScanEntry` for every non-ignored file and directory. Symlinks to
        files or directories are yielded (as what they point to) but a
        symlinked or junctioned directory is never entered. Broken symlinks
        and special files (FIFOs, sockets, devices) are not yielded.
        Directories that cannot be read are skipped silently.
    """

    # 1. Directories still to be listed, each with its depth (iterative — no recursion limit)
    pending: list[tuple[str, int]] = [(os.fspath(root), 0)]

    # 2. List one directory at a time
    while pending:
        directory, depth = pending.pop()

        # 2.1 A directory that cannot be opened is skipped
        try:
            entries = os.scandir(directory)
        except OSError:
            continue

        # 2.2 Inspect its entries; a failure while listing ends only this directory
        with entries:
            try:
                for entry in entries:

                    # 2.2.1 Ignored names are skipped entirely — no yield, no descent
                    if is_ignored(entry.name):
                        continue

                    # 2.2.2 Learn the entry's kind (symlinks are followed for the answer)
                    try:
                        is_dir = entry.is_dir()
                        is_file = not is_dir and entry.is_file()
                        enter = is_dir and depth < max_depth and not is_link_like(entry)
                    except OSError:
                        continue

                    # 2.2.3 Neither a file nor a directory — broken symlink, FIFO, device, ...
                    if not (is_dir or is_file):
                        continue

                    # 2.2.4 Yield the entry, then queue real directories within the depth limit
                    yield ScanEntry(Path(entry.path), is_file, is_dir)
                    if enter:
                        pending.append((entry.path, depth + 1))

            except OSError:
                continue


_DESIGN_NOTES = """
# walk_tree — the Shared Walker Behind Every Scanner

## Purpose
One place that knows how to traverse a directory tree safely. `iter_paths`,
`collect_paths`, `collect_files` and `collect_dirs` all sit on it.

---

## 1. Rewritten on `os.scandir`, Iterative
The old version used recursive `Path.iterdir()` generators plus separate
`is_dir()`/`is_symlink()` calls per entry, and `collect_paths` asked the disk
twice more. `os.scandir` returns the entry type with the listing itself, so
each entry costs no extra syscall for its kind (on Windows none at all), and
the `ScanEntry` carries that answer to the caller. A work list instead of
recursion means a very deep tree cannot hit Python's recursion limit.

## 2. Errors: Skipped Here, Reported at the Root
A normal tree contains unreadable folders (permissions, sync placeholders);
dying on the first one would make scanning home directories impractical, so
`walk_tree` skips them. The old version also lost the *rest* of a directory
when one entry failed; now only the failing entry is skipped. An unreadable
**root** is caught before the walk (`resolve_scan_root`) so it cannot masquerade
as an empty result.

## 3. Ignoring Applies to Files and Directories
`is_ignored(name)` is asked for every entry. An ignored directory is neither
yielded nor entered, which is what makes `.git` and `node_modules` cheap.

## 4. Symlinks and Junctions
A symlink to a directory is reported (it *is* a directory to the caller) but
not entered, so link cycles and escapes from the tree are impossible.
Windows junctions get the same treatment via `is_link_like`.

## 5. Pre-Order Within a Directory, No Global Order
Entries of a directory are yielded in the order the OS lists them, and
directories are processed last-queued-first. No order is promised —
`collect_paths` sorts; `iter_paths` documents that it does not.

## 6. No `@validate_call`
Internal helper, called with arguments the scanners have already validated.
Re-validating a set of names on every directory (as the old version did)
was pure overhead on the hottest path.
"""
