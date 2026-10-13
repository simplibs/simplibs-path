from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


class IsSymlink(Rule):
    """Path itself must be a symbolic link (working or broken).

    Rule:
        Path(value).is_symlink()

    Example:
        exclude_filter = IsSymlink()
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Ask the filesystem — a refusal or a non-path is simply a failed check
        return check_path(value, Path.is_symlink)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "symbolic link"

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
            error_name="IS_SYMLINK_ERROR",
            expected="a symbolic link",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not a symbolic link.",
            how_to_fix="Provide a path to a symbolic link.",
        )


_DESIGN_NOTES = """
# IsSymlink — Symbolic link

## Purpose
The only rule that looks at the *link* instead of its target — which is why
it also accepts a broken link that `PathExists` rejects.

## Windows
Creating symlinks needs privileges there, but *detecting* them does not.
Directory junctions are reparse points, not symlinks, and answer `False`.

## Description
`describe()` returns "symbolic link" — a short noun phrase containers compose into larger texts ("not symbolic link", "... & symbolic link"); the failure card keeps its own `expected` sentence.
"""
