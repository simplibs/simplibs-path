from pathlib import Path
from typing import Any
from simplibs.rules import Rule
# Outers
from .._helpers import build_path_rule_exception, check_path


def _is_empty_file(path: Path) -> bool:
    """True for a regular file of size zero."""
    return path.is_file() and path.stat().st_size == 0


class IsEmptyFile(Rule):
    """Path must be an existing regular file of size zero.

    Rule:
        Path(value).is_file() and Path(value).stat().st_size == 0

    Example:
        exclude_filter = IsEmptyFile()
    """

    __slots__ = ()

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Ask the filesystem — a refusal or a non-path is simply a failed check
        return check_path(value, _is_empty_file)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Fixed noun phrase
        return "empty file"

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
            error_name="IS_EMPTY_FILE_ERROR",
            expected="an existing empty file",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not an existing, empty file.",
            how_to_fix="Provide a path to an existing file whose size is zero bytes.",
        )


_DESIGN_NOTES = """
# IsEmptyFile — Empty file

## Purpose
Skipping files that carry no content (`exclude_filter=IsEmptyFile()`), or
asserting that a file was just created.

## Size, Not Content
A file with a single space is not empty. Whitespace-only content is a
question for the file library, which reads content.

## Description
`describe()` returns "empty file" — a short noun phrase containers compose into larger texts ("not empty file", "... & empty file"); the failure card keeps its own `expected` sentence.
"""
