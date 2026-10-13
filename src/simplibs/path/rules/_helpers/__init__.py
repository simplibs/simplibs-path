from .PathPartIs import PathPartIs
from .build_not_a_path_exception import build_not_a_path_exception
from .build_path_rule_exception import build_path_rule_exception
from .check_path import check_path


_DESIGN_NOTES = """
# Path Rules Internal Helpers Sub-Package

## Purpose
Building blocks shared by the rules in `lexical/` and `filesystem/`.

## Internal Components Registry

| Component                    | Type  | Description                                                              |
| :--------------------------- | :---- | :----------------------------------------------------------------------- |
| `PathPartIs`                 | Class | Base of the lens rules (`NameIs`, `StemIs`, `ParentNameIs`).             |
| `build_not_a_path_exception` | Function | Failure card for a value that is not a usable path.                   |
| `build_path_rule_exception`  | Function | A path rule's whole `build_exception`, from its three sentences.      |
| `check_path`                 | Function | Runs a filesystem check and answers `False` instead of raising.       |
"""
