from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks._helpers import to_path
from ...logic.checks import is_path_writable
from .._helpers import build_path_rule_exception


class IsPathWritable(Rule):
    """Path must be writable now, without anything being created or changed.

    Rule:
        is_path_writable(value)

    Example:
        validate(target, IsPathWritable())
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
        return is_path_writable(path, _validate_call=False)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "writable path"

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
            error_name="IS_PATH_WRITABLE_ERROR",
            expected="a writable file or directory, or a new file in a writable directory",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not writable (access is denied, its folder is missing, or the name is taken by something else).",
            how_to_fix="Provide a path you have permission to write to, inside an existing directory.",
        )


_DESIGN_NOTES = """
# IsPathWritable — Writable path

## Moved and Corrected
This rule existed in `rules/IsPathWritable.py` and delegated to a function
that **created an empty file** for a path that did not exist. The function
now probes without a trace (see `is_path_writable`), so the rule is safe to
use as a pure check. The `error_name` follows the rules library's
`<NAME>_ERROR` convention (`IS_PATH_WRITABLE_ERROR`, formerly
`PATH_NOT_WRITABLE_ERROR`).

## Accepted Values
An existing file, an existing directory, or a path of a not-yet-existing file
whose parent directory exists and accepts new files. A missing parent is
`False`: creating it is `ensure_parent_dir`'s job.

## Description
`describe()` returns "writable path" — a short noun phrase containers compose into larger texts ("not writable path", "... & writable path"); the failure card keeps its own `expected` sentence.
"""
