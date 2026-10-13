from .is_valid_suffix import is_valid_suffix
from .split_name import split_name


_DESIGN_NOTES = """
# Path Transformers Internal Helpers Sub-Package

## Purpose
Small helpers private to `transformers/`.

## Internal Components Registry

| Component         | Type     | Description                                                                |
| :---------------- | :------- | :------------------------------------------------------------------------- |
| `is_valid_suffix` | Function | Whether a string has the shape of a file suffix (`""`, `.txt`, `.tar.gz`). |
| `split_name`      | Function | Splits a final name into base name and suffix (`.tar.gz` aware).           |
"""
