from .change_suffix import change_suffix
from .make_unique_path import make_unique_path
from .normalize_entry_path import normalize_entry_path
from .normalize_path import normalize_path
from .rebase_path import rebase_path
from .relativize_path import relativize_path


_DESIGN_NOTES = """
# Path Transformers Sub-Package

## Purpose
Functions that turn one path into another: normalize it, change its suffix,
move it between two root directories, express it relative to a root, or find
a free name for it. None of them changes the disk.

## Internal Components Registry

| Component               | Type     | Description                                                           |
| :---------------------- | :------- | :-------------------------------------------------------------------- |
| `change_suffix`         | Function | Replaces, adds or removes the last suffix of a path.                  |
| `make_unique_path`      | Function | Returns a path, or a numbered variant of it, that does not exist yet. |
| `normalize_entry_path`  | Function | Resolves the directory part while preserving the entry's final name.  |
| `normalize_path`        | Function | Absolute, `~`-expanded, collapsed (and by default resolved) path.     |
| `rebase_path`           | Function | Maps a path from a source root to a target root.                      |
| `relativize_path`       | Function | Expresses a path relative to a root.                                  |
"""
