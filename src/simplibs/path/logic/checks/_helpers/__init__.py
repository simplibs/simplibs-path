from .can_create_inside import can_create_inside
from .find_filename_problem import find_filename_problem
from .to_path import to_path


_DESIGN_NOTES = """
# Path Checks Internal Helpers Sub-Package

## Purpose
Building blocks private to `checks/`.

## Internal Components Registry

| Component                    | Type     | Description                                                            |
| :--------------------------- | :------- | :--------------------------------------------------------------------- |
| `can_create_inside`          | Function | Probes whether a file can be created in a directory, leaving no trace. |
| `find_filename_problem`      | Function | Why a string is not a usable file name (`None` if it is).              |
| `_find_length_problem`       | Function | Why a name is too long for POSIX and/or Windows.                       |
| `_find_windows_name_problem` | Function | Windows-specific name problems (forbidden characters, device names).   |
| `to_path`                    | Function | Safely converts a candidate (`str` or `Path`) into a `Path` or `None`. |
"""