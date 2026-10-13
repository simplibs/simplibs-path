from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


class IsFile(Rule):
    """Path must be an existing regular file (or a symlink to one).

    Rule:
        Path(value).is_file()

    Example:
        include_filter = IsFile() & HasSuffix(".py")
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Ask the filesystem — a refusal or a non-path is simply a failed check
        return check_path(value, Path.is_file)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "existing file"

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
            error_name="IS_FILE_ERROR",
            expected="an existing file",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not an existing file.",
            how_to_fix="Provide a path to an existing regular file.",
        )


_DESIGN_NOTES = """
# IsFile — Existing file

## Purpose
"Is this a file I can treat as one?" — typically the first gate of a
pipeline step that reads content.

## Follows Symlinks
A symlink to a file is a file; a broken symlink, a directory, a FIFO or a
device is not.

## Never Raises
`Path.is_file()` itself re-raises `PermissionError` for a path behind a folder
you may not enter; `check_path` turns that into `False`, as `Rule.is_valid`
requires.

## Description
`describe()` returns "existing file" — a short noun phrase containers compose into larger texts ("not existing file", "... & existing file"); the failure card keeps its own `expected` sentence.
"""
