from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from .normalize_path import normalize_path
from ._validations import raise_path_has_no_name_error


@validate_call
def normalize_entry_path(
    path: PathLike,
) -> Path:
    """Normalize the path of a directory ENTRY — resolve its folder, keep its own name as written.

    `normalize_path` follows symlinks all the way, which is right when you mean
    "the content behind this path". This function is for operations on the
    *entry itself* — deleting, renaming, moving, checking whether a name is
    taken — where a symlink in the final position must stay a symlink:
    `delete_file("link")` must remove the link, not the file it points to.

    Args:
        path: The path of the entry.

    Returns:
        An absolute `Path`: `~` expanded, relative parts collapsed, symlinks
        in the *directory part* resolved, the final name untouched. The entry
        does not have to exist.

    Raises:
        ParamError: If `path` has no final name (a filesystem root).
        AccessError: If the directory part cannot be resolved.
    """

    # 1. Make the path absolute without following a symlink in its final name
    lexical = normalize_path(path, resolve_symlinks=False)

    # 2. A nameless path (a root) is not an entry that can be addressed by name
    if not lexical.name:
        raise_path_has_no_name_error(lexical)

    # 3. Resolve only the directory part — the final name stays as written
    return normalize_path(lexical.parent) / lexical.name


_DESIGN_NOTES = """
# normalize_entry_path — Normalizing a Name, Not Its Target

## Purpose
Two different questions hide behind "normalize this path":
* *Where is the content?* — `normalize_path` (symlinks resolved all the way).
* *Which directory entry is this?* — this function (the folder resolved, the
  final name kept).

Operations on entries (`delete_file`, `move_file`, `make_unique_path`) need the
second one; reading and writing content needs the first.

## Extracted From `make_unique_path`
`make_unique_path` already contained exactly this logic inline (a dangling link
`out.txt -> nowhere` must be judged as the name `out.txt`, not as `.../nowhere`).
It now calls this function, and `simplibs-file` shares it.

## Why Not `normalize_path(resolve_symlinks=False)`
That is purely lexical: a symlinked *directory* above the entry stays
unresolved, so two spellings of the same folder compare as different. Resolving
the directory part (and only that) gives one canonical address per entry.
"""
