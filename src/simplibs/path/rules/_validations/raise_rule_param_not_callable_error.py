from typing import Any, NoReturn
from simplibs.exception import ParamError


def raise_rule_param_not_callable_error(
    rule_name: str,
    param_name: str,
    value: Any,
) -> NoReturn:
    """Raise ParamError when a rule's rule-or-callable parameter is not callable."""

    # 1. Raise structured ParamError wrapping a TypeError
    raise ParamError(
        error_name="RULE_PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.{param_name}",
        value=value,
        problem=(
            f"Parameter '{param_name}' of {rule_name}() must be a Rule or a callable, "
            f"got {value!r} of type '{type(value).__name__}'.",
        ),
        expected="A Rule instance or a callable taking one value and returning a bool.",
        how_to_fix=(
            f"Pass a Rule (e.g. StartsWith('test_')) or a function as '{param_name}'.",
        ),
        exception=TypeError,
    )


_DESIGN_NOTES = """
# raise_rule_param_not_callable_error — Operand Guard

## Purpose
`NameIs`, `StemIs` and `ParentNameIs` wrap another rule. A value that is not
callable (a string, `None`) could never be evaluated, so it is reported when
the rule is built, not on first use.
"""
