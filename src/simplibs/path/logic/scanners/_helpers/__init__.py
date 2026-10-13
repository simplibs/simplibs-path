from .as_path_predicate import as_path_predicate
from .build_ignore_matcher import build_ignore_matcher
from .generate_paths import generate_paths
from .is_link_like import is_link_like
from .resolve_scan_root import resolve_scan_root
from .scan_paths import scan_paths
from .ScanEntry import ScanEntry
from .walk_tree import walk_tree


_DESIGN_NOTES = """
# Path Scanners Internal Helpers Sub-Package

## Purpose
The building blocks shared by `iter_paths`, `collect_paths`, `collect_files`,
`collect_dirs` and `filter_paths`.

## Internal Components Registry

| Component              | Type       | Description                                                            |
| :--------------------- | :--------- | :--------------------------------------------------------------------- |
| `as_path_predicate`    | Function   | Resolves a Rule or callable filter into one fast `(Path) -> bool`.     |
| `build_ignore_matcher` | Function   | Compiles ignore names and glob patterns into an `is_ignored(name)`.    |
| `generate_paths`       | Function   | The type-selection and filter loop over `walk_tree`.                   |
| `is_link_like`         | Function   | Symlink or Windows junction — a directory not to be entered.           |
| `resolve_scan_root`    | Function   | Normalizes a root and checks it exists, is a directory, is listable.   |
| `scan_paths`           | Function   | Prepares a scan eagerly and returns the lazy result iterator.          |
| `ScanEntry`            | NamedTuple | A found path with its kind (file or directory).                        |
| `walk_tree`            | Function   | The `os.scandir`-based, iterative tree walker.                         |
"""
