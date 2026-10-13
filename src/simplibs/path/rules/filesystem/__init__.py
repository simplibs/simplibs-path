from .IsDir import IsDir
from .IsEmptyDir import IsEmptyDir
from .IsEmptyFile import IsEmptyFile
from .IsFile import IsFile
from .IsPathReadable import IsPathReadable
from .IsPathWritable import IsPathWritable
from .IsSymlink import IsSymlink
from .PathExists import PathExists


_DESIGN_NOTES = """
# Path Filesystem Rules Sub-Package

## Purpose
Rules that ask the filesystem about a path. Each is a thin wrapper: pathlib
(or a function from `checks/`) answers, `check_path` guarantees a strict
`bool` without exceptions, and a shared helper builds the failure card.

## Internal Components Registry

| Component        | Type | Description                                                    |
| :--------------- | :--- | :------------------------------------------------------------- |
| `IsDir`          | Rule | An existing directory (or a symlink to one).                   |
| `IsEmptyDir`     | Rule | An existing directory with no entries.                         |
| `IsEmptyFile`    | Rule | An existing regular file of size zero.                         |
| `IsFile`         | Rule | An existing regular file (or a symlink to one).                |
| `IsPathReadable` | Rule | A file that can be read or a directory that can be listed.     |
| `IsPathWritable` | Rule | A path that could be written to now, with no side effects.     |
| `IsSymlink`      | Rule | The path itself is a symbolic link.                            |
| `PathExists`     | Rule | Something exists at the path.                                  |
"""
