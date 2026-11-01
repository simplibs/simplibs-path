from pathlib import Path
from typing import Any, Callable
from simplibs.exception import ValidationError
from simplibs.rules import AllOf, AnyOf, Compose, Rule, UserRule
# Outers
from ...logic.checks._helpers import to_path
from .._validations import raise_rule_param_not_callable_error
# Inners
from .build_not_a_path_exception import build_not_a_path_exception


class PathPartIs(Rule):
    """Base of the rules that check one text part of a path with another rule.

    A subclass names the part (`_part_name`) and extracts it (`_get_part`);
    everything else — validation, evaluation, description, failure card —
    is shared. Not meant to be used directly.
    """

    __slots__ = ("rule",)

    _part_name: str = "part"

    # ----------------------------------------------------------------------
    # Part extraction (the one thing a subclass defines)
    # ----------------------------------------------------------------------
    @staticmethod
    def _get_part(path: Path) -> str:
        raise NotImplementedError

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(self, rule: Rule | Callable[[Any], bool]) -> None:

        # 1. Parameter validation
        if not callable(rule):
            raise_rule_param_not_callable_error(type(self).__name__, "rule", rule)

        # 2. A plain callable gets the missing Rule contract (describe, build_exception)
        self.rule = rule if isinstance(rule, Rule) else UserRule(rule)

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. Let the wrapped rule judge the extracted text
        return bool(self.rule.is_valid(self._get_part(path)))

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. The wrapped rule describes itself — a faulty describe() must never break this one
        # noinspection PyBroadException
        try:
            text = self.rule.describe()
        except Exception:
            text = None
        if not isinstance(text, str) or not text:
            text = type(self.rule).__name__

        # 2. A compound operand needs parentheses so the prefix reads as covering all of it
        if isinstance(self.rule, (AllOf, AnyOf, Compose)):
            text = f"({text})"

        # 3. "name: <rule>"
        return f"{self._part_name}: {text}"

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. Prepare data
        prefix = f"{self._part_name.upper().replace(' ', '_')}_IS"

        # 2. Not a usable path at all
        path = to_path(value)
        if path is None:
            return build_not_a_path_exception(
                error_name=f"{prefix}_ERROR",
                expected=f"a path whose {self.describe()}",
                value=value,
                value_name=value_name,
                context=context,
            )

        # 3. The part fails the wrapped rule — vend the wrapped rule's own card
        part = self._get_part(path)
        if not self.rule.is_valid(part):
            label = f"{value_name}.{self._part_name}" if value_name else self._part_name
            return self.rule.build_exception(part, value_name=label, context=context)

        # 4. Fallback (build exception if the part unexpectedly passed)
        return ValidationError(
            error_name=f"{prefix}_UNREACHABLE_ERROR",
            label=value_name,
            expected=f"a path whose {self.describe()}",
            value=value,
            problem="The path part unexpectedly passed during error construction.",
            context=context,
            how_to_fix=("Check validation logic state.",),
            exception=RuntimeError,
        )


_DESIGN_NOTES = """
# PathPartIs — a Lens From a Path to One of Its Text Parts

## Purpose
Matching file names ("starts with `test_`", "matches this regex") needs no
new string logic: `StartsWith`, `Regex`, `Contains` and every other string
rule already exists. `NameIs(StartsWith("test_"))` simply points them at the
right piece of the path. The lenses (`NameIs`, `StemIs`, `ParentNameIs`,
`AnyParentNameIs`) differ only in which piece; this base holds the rest.

---

## 1. Plain Callables Are Wrapped in `UserRule`
Same reasoning as `validate_call`'s `overrides`: a bare function has no
`describe()` and no `build_exception()`, so a failure could not be
explained. `UserRule` supplies both.

## 2. The Failure Card Is the Wrapped Rule's Own
`NameIs(StartsWith("test_"))` on `src/a.py` reports *that `a.py` does not
start with `test_`*, labelled `source.name` — the same "delegate to
whoever actually failed" principle `AllOf` and `ForEach` use. Consequently
`exc.value` is the part, not the whole path (contract tests run with
`check_value=False`).

## 3. Description
`name: string starting with 'test_'`. A compound operand is wrapped in
parentheses (`name: (a | b)`), exactly as `ForEach` does for `each (a | b)`.

## 4. Why a Base Class and Not Three Copies
The three rules are 90% identical; a bug fixed in one (say, how the label
is built) must be fixed in all. `__slots__` is declared on the base and
as `()` on each subclass, so no instance carries a `__dict__`.
"""
