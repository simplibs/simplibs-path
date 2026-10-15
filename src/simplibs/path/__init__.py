from .logic.checks import (
    is_empty_dir,
    is_hidden_path,
    is_path_readable,
    is_path_writable,
    is_valid_filename,
    is_within,
)
from .logic.ensure import (
    ensure_dir,
    ensure_file,
    ensure_parent_dir,
)
from .logic.scanners import (
    DEFAULT_IGNORE_NAMES,
    IGNORE_BUILD,
    IGNORE_ENV,
    IGNORE_GENERIC,
    IGNORE_IDE,
    IGNORE_SYSTEM,
    IGNORE_VCS,
    collect_dirs,
    collect_files,
    collect_paths,
    filter_paths,
    iter_paths,
)
from .logic.transformers import (
    change_suffix,
    make_unique_path,
    normalize_path,
    normalize_entry_path,
    rebase_path,
    relativize_path,
)
from .annotations import (
    PathLike,
    PathPredicate,
    RecursionDepth,
)

__all__ = [
    # transformers — path in, path out
    "normalize_entry_path",
    "normalize_path",
    "rebase_path",
    "relativize_path",
    "change_suffix",
    "make_unique_path",
    # checks — a bool, never an exception for disk problems
    "is_empty_dir",
    "is_hidden_path",
    "is_path_readable",
    "is_path_writable",
    "is_valid_filename",
    "is_within",
    # ensure — make a filesystem state true
    "ensure_dir",
    "ensure_file",
    "ensure_parent_dir",
    # scanners — look at a directory tree
    "collect_paths",
    "collect_files",
    "collect_dirs",
    "iter_paths",
    "filter_paths",
    "DEFAULT_IGNORE_NAMES",
    "IGNORE_BUILD",
    "IGNORE_ENV",
    "IGNORE_GENERIC",
    "IGNORE_IDE",
    "IGNORE_SYSTEM",
    "IGNORE_VCS",
    # annotations — types for your own signatures
    "PathLike",
    "PathPredicate",
    "RecursionDepth",
]


_DESIGN_NOTES = """
# simplibs-path — Package Root

## Purpose
Safe, composable work with paths and directory trees: normalize, check,
ensure and scan — as plain functions, as `Rule`s, and as pipeline `Action`s.

## What the Root Exports
Everything from the four logic sub-packages of `logic/`
(`transformers`, `checks`, `ensure`, `scanners`) and the three public
types of `annotations/`:

    from simplibs.path import collect_files, normalize_path, PathLike

## What the Root Deliberately Does NOT Export
* **`rules/` and `actions/`** — domain folders with their own `__all__`,
  imported through their domain:

      from simplibs.path.rules import HasSuffix, IsFile
      from simplibs.path.actions import CollectFiles

  Twenty-nine class names would drown the thirty-odd functions, and a
  `Rule` and an `Action` are different kinds of thing that should stay
  visibly different at the import line.
* **`ScanEntry`** — the walker's internal result type; it never appears in
  a public signature.

## Why the Three Types ARE Exported
`PathLike`, `PathPredicate` and `RecursionDepth` are annotations meant for
the caller's own signatures (`def load(path: PathLike) -> ...`), always used
together with the functions. They are few, tiny and unambiguous — unlike
the rules and actions — so the root is the natural place for them. They stay
importable from `simplibs.path.annotations` as well.

## `__all__`
Defined here and in the domain folders (`rules`, `actions`) only; the
sub-packages below export by plain imports.
"""
