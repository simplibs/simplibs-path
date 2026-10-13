from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


class IsDir(Rule):
    """Path must be an existing directory (or a symlink to one).

    Rule:
        Path(value).is_dir()

    Example:
        validate(root, IsDir())  # or: IsDir() >> CollectFiles()
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Ask the filesystem — a refusal or a non-path is simply a failed check
        return check_path(value, Path.is_dir)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "existing directory"

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
            error_name="IS_DIR_ERROR",
            expected="an existing directory",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not an existing directory.",
            how_to_fix="Provide a path to an existing directory.",
        )


_DESIGN_NOTES = """
# IsDir — Existing directory

## Purpose
The natural head of a pipeline: `IsDir() >> CollectFiles()` — check the
input, then pass it on unchanged (`Action` turns the rule into a `guard`).

## Follows Symlinks
A symlink to a directory is a directory here, as for every pathlib call.

## Description
`describe()` returns "existing directory" — a short noun phrase containers compose into larger texts ("not existing directory", "... & existing directory"); the failure card keeps its own `expected` sentence.
"""
