from .raise_invalid_suffix_error import raise_invalid_suffix_error
from .raise_normalize_path_error import raise_normalize_path_error
from .raise_path_has_no_name_error import raise_path_has_no_name_error
from .raise_path_not_within_root_error import raise_path_not_within_root_error
from .raise_unique_path_exhausted_error import raise_unique_path_exhausted_error


_DESIGN_NOTES = """
# Path Transformers Diagnostic Helpers Sub-Package

## Purpose
Internal diagnostic helpers raising structured exceptions for the functions
in `transformers/`.

## Internal Components Registry

| Component                           | Type     | Description                                                              |
| :---------------------------------- | :------- | :----------------------------------------------------------------------- |
| `raise_invalid_suffix_error`        | Function | Raises `ParamError` for a malformed new suffix (`change_suffix`).        |
| `raise_normalize_path_error`        | Function | Raises `AccessError` when a path cannot be resolved (`normalize_path`).  |
| `raise_path_has_no_name_error`      | Function | Raises `ParamError` for a root, `.` or `..` (`change_suffix`, `make_unique_path`). |
| `raise_path_not_within_root_error`  | Function | Raises `ParamError` when a path is outside its root (`rebase_path`, `relativize_path`). |
| `raise_unique_path_exhausted_error` | Function | Raises `OperationError` when no free numbered name exists (`make_unique_path`). |
"""
