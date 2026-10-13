from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks._helpers import to_path
from ...logic.checks import is_path_readable
from .._helpers import build_path_rule_exception


class IsPathReadable(Rule):
    """Path must be a file that can be read or a directory that can be listed.

    Rule:
        is_path_readable(value)

    Example:
        validate(source, IsPathReadable())
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
        return is_path_readable(path, _validate_call=False)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "readable path"

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
            error_name="IS_PATH_READABLE_ERROR",
            expected="a readable file or directory",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not readable (it is missing, not a regular file or directory, or access is denied).",
            how_to_fix="Provide a path to a file or directory you have permission to read.",
        )


_DESIGN_NOTES = """
# IsPathReadable — Readable path

## Purpose
A precondition for any step that reads: the failure card says *readable*, so
a permission problem is not mistaken for a missing file.

## Delegates to `is_path_readable`
It actually opens the file (or lists the directory) — the only check that
agrees with the real read that follows.

## Description
`describe()` returns "readable path" — a short noun phrase containers compose into larger texts ("not readable path", "... & readable path"); the failure card keeps its own `expected` sentence.
"""
