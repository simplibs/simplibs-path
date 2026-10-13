from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.transformers._helpers import is_valid_suffix
from ...logic.checks._helpers import to_path
from .._helpers import build_path_rule_exception
from .._validations import (
    raise_has_suffix_invalid_suffix_error,
    raise_has_suffix_no_suffixes_error,
    raise_rule_param_not_bool_error,
)


class HasSuffix(Rule):
    """Path must end with one of the given suffixes.

    Rule:
        the final name ends with one of `suffixes` (after a non-empty base name)

    Example:
        validate(path, HasSuffix(".py"))
        include_filter = HasSuffix(".py", ".md")
        HasSuffix("")        # names without any suffix
    """

    __slots__ = ("suffixes", "ignore_case", "_keys")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, *suffixes: str, ignore_case: bool = True) -> None:

        # 1. Parameter validation
        if not suffixes:
            raise_has_suffix_no_suffixes_error()
        for suffix in suffixes:
            if not isinstance(suffix, str) or not is_valid_suffix(suffix):
                raise_has_suffix_invalid_suffix_error(suffix)
        if not isinstance(ignore_case, bool):
            raise_rule_param_not_bool_error("HasSuffix", "ignore_case", ignore_case)

        # 2. Parameter assignment, with the comparison keys prepared once
        self.suffixes = tuple(suffixes)
        self.ignore_case = ignore_case
        self._keys = tuple(suffix.casefold() for suffix in suffixes) if ignore_case else self.suffixes

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. Compare the final name with each suffix
        name = path.name.casefold() if self.ignore_case else path.name
        for key in self._keys:

            # 2.1 An empty suffix means "the name has no suffix at all"
            if key == "":
                if path.suffix == "":
                    return True

            # 2.2 Otherwise the name must end with it, after a non-empty base name
            elif len(name) > len(key) and name.endswith(key):
                return True

        # 3. No suffix matched
        return False

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. One suffix reads "suffix '.py'", several "suffix one of '.py', '.md'"
        if len(self.suffixes) == 1:
            text = f"suffix {self.suffixes[0]!r}"
        else:
            text = "suffix one of " + ", ".join(repr(suffix) for suffix in self.suffixes)

        # 2. Say so when the comparison is case-sensitive
        return text if self.ignore_case else f"{text} (case-sensitive)"

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
            error_name="HAS_SUFFIX_ERROR",
            expected=f"a path with {self.describe()}",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} does not have {self.describe()}.",
            how_to_fix=f"Provide a path with {self.describe()}.",
        )


_DESIGN_NOTES = """
# HasSuffix — Select by File Extension

## Purpose
The most common filter of an extraction pipeline: "only `.py` and `.md`".
`include_filter=HasSuffix(".py", ".md")`.

---

## 1. Matches the End of the Name, Not `Path.suffix`
`Path("a.tar.gz").suffix` is only `.gz`, so `HasSuffix(".tar.gz")` could never
match by comparing it. Checking `name.endswith(suffix)` supports compound
suffixes. A name that *is* the suffix (`.py` as a whole file name, which is a
hidden file without an extension) does not match — a suffix needs a base name
in front of it.

## 2. `""` Means "No Suffix"
`HasSuffix("")` selects names without an extension (`Makefile`, `.bashrc`).
It is the one case compared through `Path.suffix`.

## 3. Case-Insensitive by Default
`README.MD` and `x.PY` are what Windows users produce; a filter that misses
them is a surprise. `ignore_case=False` opts out. `casefold` is used instead
of `lower` for correct Unicode comparison.

## 4. Lexical — Works on Names, Not on Files
`HasSuffix(".py")` is true for a *directory* named `pkg.py` too. Combine
with `IsFile()` when the type matters: `IsFile() & HasSuffix(".py")`.

## 5. Constructor Guards
No suffixes, a suffix without a leading dot (`"py"` would match any name
ending in "py"), and a non-bool `ignore_case` are all `ParamError`s. The
shape check is `is_valid_suffix`, shared with `change_suffix`.

## 6. Description
`suffix '.py'` / `suffix one of '.py', '.md'` — no `|` in the text, so the
description cannot be misread inside `a | b`/`a & b` compositions.
"""
