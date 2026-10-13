from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_rule_param_not_path_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> NoReturn:
    """Raise ParamError when a rule's path constructor parameter is not a usable path."""

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="RULE_PARAM_NOT_PATH_ERROR",
        label=f"{rule_name}.{param_name}",
        value=value,
        problem=(
            f"Parameter '{param_name}' of {rule_name}() must be a non-blank str or a Path "
            f"without a null byte, got {value!r} of type '{type(value).__name__}'.",
        ),
        expected="A non-blank string or a Path instance.",
        how_to_fix=(
            f"Pass a directory path as '{param_name}', e.g. Path('src') or 'src'.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_rule_param_not_path_error — Path Option Guard

## Purpose
`IsWithin(root)` is meaningless with a blank or non-path root (it would
quietly mean "the current directory" or never match). The same `to_path`
conversion the rule uses at evaluation time decides here, so "accepted at
construction" and "usable at evaluation" cannot disagree.
"""
