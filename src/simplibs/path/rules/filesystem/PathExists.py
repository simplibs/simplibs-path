from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


class PathExists(Rule):
    """Path must exist (a file, a directory, or a symlink that leads somewhere).

    Rule:
        Path(value).exists()

    Example:
        validate(path, PathExists())
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Ask the filesystem — a refusal or a non-path is simply a failed check
        return check_path(value, Path.exists)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "existing path"

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
            error_name="PATH_EXISTS_ERROR",
            expected="an existing path",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} does not exist.",
            how_to_fix="Provide a path to an existing file or directory.",
        )


_DESIGN_NOTES = """
# PathExists — Existing path

## Purpose
The most basic filesystem precondition: "is there anything at this path?".

## Follows Symlinks
`Path.exists()` follows links, so a *broken* symlink answers `False` — the
thing it points at is missing. `IsSymlink` is the rule that sees the link
itself.

## A Check at One Moment
The answer holds when evaluated; the file can appear or vanish right after.
Use it as a fail-fast message, not as a guarantee (see `ensure_file`).

## Description
`describe()` returns "existing path" — a short noun phrase containers compose into larger texts ("not existing path", "... & existing path"); the failure card keeps its own `expected` sentence.
"""
