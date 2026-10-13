from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks._helpers import to_path
from ...logic.checks import is_hidden_path
from .._helpers import build_path_rule_exception
from .._validations import raise_rule_param_not_bool_error


class IsHidden(Rule):
    """Path must be hidden — its final name starts with a dot.

    Rule:
        is_hidden_path(value)

    Example:
        exclude_filter = IsHidden()
        IsHidden(check_attributes=True)    # also the Windows "hidden" attribute
    """

    __slots__ = ("check_attributes",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *, check_attributes: bool = False) -> None:

        # 1. Parameter validation
        if not isinstance(check_attributes, bool):
            raise_rule_param_not_bool_error("IsHidden", "check_attributes", check_attributes)

        # 2. Parameter assignment
        self.check_attributes = check_attributes

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. Delegate to the plain predicate (its own validation is skipped — the input is checked)
        return is_hidden_path(path, check_attributes=self.check_attributes, _validate_call=False)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "hidden path"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Build the exception (the not-a-path branch is handled by the helper)
        return build_path_rule_exception(
            error_name="IS_HIDDEN_ERROR",
            expected="a hidden path (its name starts with a dot)",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not hidden.",
            how_to_fix="Provide a path whose final name starts with a dot, such as '.git'.",
        )


_DESIGN_NOTES = """
# IsHidden — Hidden by Name, Optionally by Windows Attribute

## Purpose
Mostly used negated: `exclude_filter=IsHidden()` or `include_filter=~IsHidden()`.

## Final Name Only
`/home/me/.config/tool/a.json` is not hidden by this rule — its name is not.
Skipping whole hidden *folders* is what a scanner's `ignore_names` does.

## Keyword-Only Option
`IsHidden(True)` would read as a mystery; `IsHidden(check_attributes=True)`
says what it does. The option costs a `stat` call per path and exists only on
Windows (a no-op elsewhere), so it is off by default.
"""
