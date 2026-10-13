from pathlib import Path
from typing import Any
from simplibs.exception import ValidationError
from simplibs.rules import Rule
# Outers
from ...logic.checks import is_valid_filename
from ...logic.checks._helpers import find_filename_problem
from .._helpers import build_not_a_path_exception
from .._validations import raise_rule_param_not_bool_error


class IsValidFilename(Rule):
    """A string must be a usable file name; for a `Path`, its final name must be.

    Rule:
        is_valid_filename(value if str else value.name)

    Example:
        validate(title + ".md", IsValidFilename())
        IsValidFilename(portable=False)     # only the current OS's rules
    """

    __slots__ = ("portable",)

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *, portable: bool = True) -> None:

        # 1. Parameter validation
        if not isinstance(portable, bool):
            raise_rule_param_not_bool_error("IsValidFilename", "portable", portable)

        # 2. Parameter assignment
        self.portable = portable

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    @staticmethod
    def _name_of(value: Any) -> str | None:
        """The text to judge: a str as it is, a Path by its final name, anything else None."""
        if isinstance(value, str):
            return value
        if isinstance(value, Path):
            return value.name
        return None

    def is_valid(self, value: Any) -> bool:

        # 1. Only a str or a Path has a name
        name = self._name_of(value)
        if name is None:
            return False

        # 2. Delegate to the plain predicate (its own validation is skipped — the input is checked)
        return is_valid_filename(name, portable=self.portable, _validate_call=False)

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Portable by default; the relaxed mode says so
        return "portable file name" if self.portable else "file name valid on this OS"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Not a str/Path at all
        name = self._name_of(value)
        if name is None:
            return build_not_a_path_exception(
                error_name="IS_VALID_FILENAME_ERROR",
                expected=f"a {self.describe()}",
                value=value,
                value_name=value_name,
                context=context,
            )

        # 2. Ask what exactly is wrong with the name
        reason = find_filename_problem(name, portable=self.portable)

        # 3. Fallback (build exception if the name was unexpectedly fine)
        if reason is None:
            return ValidationError(
                error_name="IS_VALID_FILENAME_UNREACHABLE_ERROR",
                label=value_name,
                expected=f"a {self.describe()}",
                value=value,
                problem="The name unexpectedly passed during error construction.",
                context=context,
                how_to_fix=("Check validation logic state.",),
                exception=RuntimeError,
            )

        # 4. Build the exception with the concrete reason
        return ValidationError(
            error_name="IS_VALID_FILENAME_ERROR",
            label=value_name,
            expected=f"a {self.describe()}",
            value=value,
            problem=f"{name!r} is not a usable file name ({reason}).",
            context=context,
            how_to_fix="Provide a name without separators, forbidden characters or reserved names.",
            exception=ValueError,
        )


_DESIGN_NOTES = """
# IsValidFilename — Is This Safe to Create as a File Name?

## Purpose
For output names built from content (titles, ids): validate before writing,
and get a card that says *why* ("contains the character '?', which Windows
forbids in names").

## A `str` Is a Name; a `Path` Is Judged by Its Final Name
`"dir/report.md"` is not a valid *name* (the separator), while
`Path("dir/report.md")` is a path whose name `report.md` is fine. Each type
means what it naturally means.

## One Source of Truth
Both `is_valid` and the card text come from `find_filename_problem`, so the
rule can never reject a name for one reason and explain it with another.

## Portable by Default
See `find_filename_problem`: the strictest union of Windows and POSIX rules.
"""
