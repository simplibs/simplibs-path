from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks._helpers import to_path
from ...logic.checks import is_empty_dir
from .._helpers import build_path_rule_exception


class IsEmptyDir(Rule):
    """Path must be an existing directory with no entries.

    Rule:
        is_empty_dir(value)

    Example:
        validate(output_dir, IsEmptyDir())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. Delegate to the plain predicate (its own validation is skipped — the input is checked)
        return is_empty_dir(path, _validate_call=False)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "empty directory"

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
            error_name="IS_EMPTY_DIR_ERROR",
            expected="an existing empty directory",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not an existing, empty directory.",
            how_to_fix="Provide a path to an existing directory that contains nothing.",
        )


_DESIGN_NOTES = """
# IsEmptyDir — Empty directory

## Purpose
"Only write into an empty folder", "this scan found nothing to clean up".

## Delegates to `is_empty_dir`
Reads the first entry only and treats an unlistable directory as *not* empty
(emptiness unknown) — see the function's notes.

## Description
`describe()` returns "empty directory" — a short noun phrase containers compose into larger texts ("not empty directory", "... & empty directory"); the failure card keeps its own `expected` sentence.
"""
