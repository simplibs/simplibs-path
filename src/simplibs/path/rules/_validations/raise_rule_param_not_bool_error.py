from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_rule_param_not_bool_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> NoReturn:
    """Raise ParamError when a rule's boolean constructor parameter is not a bool."""

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="RULE_PARAM_NOT_BOOL_ERROR",
        label=f"{rule_name}.{param_name}",
        value=value,
        problem=(
            f"Parameter '{param_name}' of {rule_name}() must be a bool, "
            f"got {value!r} of type '{type(value).__name__}'.",
        ),
        expected="True or False.",
        how_to_fix=(
            f"Pass True or False as '{param_name}'.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_rule_param_not_bool_error — Boolean Option Guard

## Purpose
`ignore_case`, `resolve_symlinks`, `allow_equal`, `portable` and
`check_attributes` are on/off switches. A truthy string such as `"yes"` would
be accepted by Python but almost certainly signals a mistake, so the rules
require a real `bool` and report anything else at construction time.
"""
