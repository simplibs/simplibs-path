from .is_empty_dir import is_empty_dir
from .is_hidden_path import is_hidden_path
from .is_path_readable import is_path_readable
from .is_path_writable import is_path_writable
from .is_valid_filename import is_valid_filename
from .is_within import is_within


_DESIGN_NOTES = """
# Path Checks Sub-Package

## Purpose
Plain predicate functions with real logic behind them. Each returns a `bool`
and never raises for disk problems; the matching `Rule` classes in `rules/`
are thin wrappers over them. Checks that are a single pathlib call
(`exists`, `is_file`, `is_dir`, ...) have no function here — the rule calls
pathlib directly.

## Internal Components Registry

| Component          | Type     | Description                                                           |
| :----------------- | :------- | :-------------------------------------------------------------------- |
| `is_empty_dir`     | Function | An existing, listable directory with no entries.                      |
| `is_hidden_path`   | Function | The final name starts with a dot (optionally: Windows hidden attribute). |
| `is_path_readable` | Function | A file that can be opened, or a directory that can be listed.         |
| `is_path_writable` | Function | A path that could be written to now — with no side effects.           |
| `is_valid_filename`| Function | A string usable as a file name (portable by default).                 |
| `is_within`        | Function | A path lies inside a root directory (symlink-safe by default).        |
"""
