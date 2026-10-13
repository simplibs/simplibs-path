from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


class IsAbsolutePath(Rule):
    """Path must be absolute.

    Rule:
        Path(value).is_absolute()

    Example:
        validate(path, IsAbsolutePath())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Pure path arithmetic — no disk access
        return check_path(value, Path.is_absolute)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "absolute path"

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
            error_name="IS_ABSOLUTE_PATH_ERROR",
            expected="an absolute path",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not absolute.",
            how_to_fix="Provide an absolute path, or make it absolute with normalize_path().",
        )


_DESIGN_NOTES = """
# IsAbsolutePath — Anchored, Not Relative

## Purpose
A precondition for steps that must not depend on the working directory.

## Platform Rule
`Path.is_absolute()` follows the platform: `/etc` is absolute on POSIX, but on
Windows it lacks a drive and is *not* (`C:\\\\etc` is). The rule reports what
the platform means by "absolute".

## `~` Is Expanded First
`to_path` expands a leading `~`, so `~/work` is absolute (it is the home
directory). A path that merely *starts with* a tilde character is otherwise
indistinguishable from a home reference, and the rest of the library treats
them identically.
"""
