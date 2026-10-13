from .collect_dirs import collect_dirs
from .collect_files import collect_files
from .collect_paths import collect_paths
from .filter_paths import filter_paths
from .iter_paths import iter_paths
from .ignore_names import (
    DEFAULT_IGNORE_NAMES,
    IGNORE_BUILD,
    IGNORE_ENV,
    IGNORE_GENERIC,
    IGNORE_IDE,
    IGNORE_SYSTEM,
    IGNORE_VCS,
)


_DESIGN_NOTES = """
# Path Scanners Sub-Package

## Purpose
Everything that looks at a directory tree: scanning it for files and
directories, and filtering lists of paths. Nothing here changes the disk.

## Internal Components Registry

| Component              | Type     | Description                                                          |
| :--------------------- | :------- | :------------------------------------------------------------------- |
| `collect_dirs`         | Function | Sorted list of the directories in a tree.                            |
| `collect_files`        | Function | Sorted list of the files in a tree.                                  |
| `collect_paths`        | Function | Sorted list of files and/or directories in a tree.                   |
| `filter_paths`         | Function | Keeps the paths of a list that satisfy a Rule or callable.           |
| `iter_paths`           | Function | Lazy, unsorted iterator over the paths of a tree.                    |
| `DEFAULT_IGNORE_NAMES` | Constant | The names every scan skips by default.                               |
| `IGNORE_*`             | Constant | The named groups it is built from (`IGNORE_GENERIC` is opt-in).      |
"""
