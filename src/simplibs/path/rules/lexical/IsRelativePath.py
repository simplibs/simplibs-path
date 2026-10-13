from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks._helpers import to_path
from .._helpers import build_path_rule_exception


class IsRelativePath(Rule):
    """Path must be relative.

    Rule:
        not Path(value).is_absolute()

    Example:
        validate(path, IsRelativePath())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails — it is not "relative" either
        path = to_path(value)
        if path is None:
            return False

        # 2. Pure path arithmetic — no disk access
        return not path.is_absolute()

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "relative path"

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
            error_name="IS_RELATIVE_PATH_ERROR",
            expected="a relative path",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is absolute.",
            how_to_fix="Provide a relative path, or make it relative with relativize_path().",
        )


_DESIGN_NOTES = """
# IsRelativePath — Not Anchored

## Purpose
The counterpart of `IsAbsolutePath` — e.g. for checking that a path taken
from a configuration file cannot point outside the project.

## Not Simply `~IsAbsolutePath()`
`~IsAbsolutePath()` would also accept `None`, `5` and `""` (anything that is
not an absolute path). A *relative path* has to be a path first, so this is
its own rule rather than a negation.
"""
