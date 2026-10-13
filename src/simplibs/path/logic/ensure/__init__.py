from .ensure_dir import ensure_dir
from .ensure_file import ensure_file
from .ensure_parent_dir import ensure_parent_dir


_DESIGN_NOTES = """
# Path Ensure Sub-Package

## Purpose
Functions that make a filesystem state true — a directory exists, a file
exists, a path's parent exists — and return the normalized path. These are
the library's only functions that change the disk (besides what the caller
writes itself), which is why they live apart from the pure `transformers/`.

## Internal Components Registry

| Component           | Type     | Description                                                              |
| :------------------ | :------- | :----------------------------------------------------------------------- |
| `ensure_dir`        | Function | Guarantees a directory exists, creating it and its parents.              |
| `ensure_file`       | Function | Guarantees a file exists, optionally creating it and its parent directory. |
| `ensure_parent_dir` | Function | Guarantees the directory a path lives in exists; returns the path itself. |
"""
