from .raise_collect_paths_not_a_dir_error import raise_collect_paths_not_a_dir_error
from .raise_collect_paths_not_found_error import raise_collect_paths_not_found_error
from .raise_collect_paths_root_unreadable_error import raise_collect_paths_root_unreadable_error
from .raise_ignore_names_not_names_error import raise_ignore_names_not_names_error
from .raise_nothing_to_collect_error import raise_nothing_to_collect_error


_DESIGN_NOTES = """
# Path Scanners Diagnostic Helpers Sub-Package

## Purpose
Internal diagnostic helpers raising structured exceptions for the tree
scanners in `scanners/`.

## Internal Components Registry

| Component                                     | Type     | Description                                                        |
| :-------------------------------------------- | :------- | :----------------------------------------------------------------- |
| `raise_collect_paths_not_a_dir_error`         | Function | Raises `StateError` when the scan root is a file.                  |
| `raise_collect_paths_not_found_error`         | Function | Raises `NotFoundError` when the scan root does not exist.          |
| `raise_collect_paths_root_unreadable_error`   | Function | Raises `AccessError` when the scan root is unreadable.             |
| `raise_ignore_names_not_names_error`          | Function | Raises `ParamError` when `ignore_names` is a single string.        |
| `raise_nothing_to_collect_error`              | Function | Raises `ParamError` when both collect flags are False.             |
"""