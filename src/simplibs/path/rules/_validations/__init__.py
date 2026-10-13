from .raise_has_suffix_invalid_suffix_error import raise_has_suffix_invalid_suffix_error
from .raise_has_suffix_no_suffixes_error import raise_has_suffix_no_suffixes_error
from .raise_rule_param_not_bool_error import raise_rule_param_not_bool_error
from .raise_rule_param_not_callable_error import raise_rule_param_not_callable_error
from .raise_rule_param_not_path_error import raise_rule_param_not_path_error


_DESIGN_NOTES = """
# Path Rules Diagnostic Helpers Sub-Package

## Purpose
Internal diagnostic helpers raising `ParamError` when a rule is constructed
with invalid arguments.

## Internal Components Registry

| Component                                | Type     | Description                                                       |
| :--------------------------------------- | :------- | :---------------------------------------------------------------- |
| `raise_has_suffix_invalid_suffix_error`  | Function | A `HasSuffix` suffix has the wrong shape.                         |
| `raise_has_suffix_no_suffixes_error`     | Function | `HasSuffix()` was created without any suffix.                     |
| `raise_rule_param_not_bool_error`        | Function | An on/off option is not a `bool`.                                 |
| `raise_rule_param_not_callable_error`    | Function | A wrapped rule/predicate is not callable.                         |
| `raise_rule_param_not_path_error`        | Function | A root/path option is not a usable path.                          |
"""
