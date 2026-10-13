from .raise_ensure_dir_error import raise_ensure_dir_error
from .raise_ensure_dir_not_a_dir_error import raise_ensure_dir_not_a_dir_error
from .raise_ensure_file_create_error import raise_ensure_file_create_error
from .raise_ensure_file_not_a_file_error import raise_ensure_file_not_a_file_error
from .raise_ensure_file_not_found_error import raise_ensure_file_not_found_error


_DESIGN_NOTES = """
# Path Ensure Diagnostic Helpers Sub-Package

## Purpose
Internal diagnostic helpers raising structured exceptions for the
functions in `ensure/` (`ensure_dir`, `ensure_file`, `ensure_parent_dir`).
These five files moved here unchanged from `validators/_validations/`.

## Internal Components Registry

| Component                              | Type     | Description                                                      |
| :------------------------------------- | :------- | :--------------------------------------------------------------- |
| `raise_ensure_dir_error`               | Function | Raises `AccessError` when a directory cannot be created.         |
| `raise_ensure_dir_not_a_dir_error`     | Function | Raises `StateError` when a file blocks a wanted directory.       |
| `raise_ensure_file_create_error`       | Function | Raises `AccessError` when a file cannot be created.              |
| `raise_ensure_file_not_a_file_error`   | Function | Raises `StateError` when a directory blocks a wanted file.       |
| `raise_ensure_file_not_found_error`    | Function | Raises `NotFoundError` for a missing file when `create=False`.   |
"""
