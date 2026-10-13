from typing import Any
from simplibs.exception import ValidationError
# Outers
from ...logic.checks._helpers import to_path
# Inners
from .build_not_a_path_exception import build_not_a_path_exception


def build_path_rule_exception(
    *,
    error_name: str,
    expected: str,
    value: Any,
    value_name: str | None,
    context: str | None,
    problem: str,
    how_to_fix: str,
    exception: type[Exception] = ValueError,
) -> Exception:
    """Build the failure card of a path rule, covering both failure branches.

    Args:
        error_name: The calling rule's `error_name`.
        expected: The calling rule's `expected` sentence.
        value: The rejected value.
        value_name: The label passed to `build_exception`.
        context: The context passed to `build_exception`.
        problem: What is wrong with a value that IS a usable path.
        how_to_fix: How to fix that.
        exception: The exception type wrapped for that case.

    Returns:
        A `ValidationError`. If `value` is not a usable path at all, the
        generic "not a path" card is returned instead of `problem`/`how_to_fix`.
    """

    # 1. Not a usable path — the shared card
    if to_path(value) is None:
        return build_not_a_path_exception(
            error_name=error_name,
            expected=expected,
            value=value,
            value_name=value_name,
            context=context,
        )

    # 2. A usable path that fails the rule's own condition
    return ValidationError(
        error_name=error_name,
        label=value_name,
        expected=expected,
        value=value,
        problem=problem,
        context=context,
        how_to_fix=how_to_fix,
        exception=exception,
    )


_DESIGN_NOTES = """
# build_path_rule_exception — the Whole `build_exception` of a Path Rule

## Purpose
Reduces a path rule's `build_exception` to its own three sentences
(`expected`, `problem`, `how_to_fix`): the type-or-blank branch is decided
here, identically for all of them.

## Keyword-Only
Seven values of the same kind (`str`) travel together; naming each at the
call site is what keeps `problem` and `how_to_fix` from being swapped.
"""
