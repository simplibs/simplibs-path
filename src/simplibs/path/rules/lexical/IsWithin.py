from typing import Any
from simplibs.rules import Rule
# Outers
from ...logic.checks import is_within
from ...logic.checks._helpers import to_path
from .._helpers import build_path_rule_exception
from .._validations import raise_rule_param_not_bool_error, raise_rule_param_not_path_error


class IsWithin(Rule):
    """Path must lie inside the given root directory.

    Rule:
        is_within(value, root)

    Example:
        validate(output_path, IsWithin("out"))
        IsWithin(root, resolve_symlinks=False, allow_equal=False)
    """

    __slots__ = ("root", "resolve_symlinks", "allow_equal")

    # ----------------------------------------------------------------------
    # Constructor initialization
    # ----------------------------------------------------------------------
    def __init__(
        self,
        root: Any,
        *,
        resolve_symlinks: bool = True,
        allow_equal: bool = True,
    ) -> None:

        # 1. Parameter validation
        if to_path(root) is None:
            raise_rule_param_not_path_error("IsWithin", "root", root)
        if not isinstance(resolve_symlinks, bool):
            raise_rule_param_not_bool_error("IsWithin", "resolve_symlinks", resolve_symlinks)
        if not isinstance(allow_equal, bool):
            raise_rule_param_not_bool_error("IsWithin", "allow_equal", allow_equal)

        # 2. Parameter assignment
        self.root = root
        self.resolve_symlinks = resolve_symlinks
        self.allow_equal = allow_equal

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. Delegate to the plain predicate (its own validation is skipped — the input is checked)
        return is_within(
            path,
            self.root,
            resolve_symlinks=self.resolve_symlinks,
            allow_equal=self.allow_equal,
            _validate_call=False,
        )

    # ----------------------------------------------------------------------
    # Description definition
    # ----------------------------------------------------------------------
    def describe(self) -> str:

        # 1. Phrase built from the rule's parameter
        return f"path within {str(self.root)!r}"

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
            error_name="IS_WITHIN_ERROR",
            expected=f"a path inside {str(self.root)!r}",
            value=value,
            value_name=value_name,
            context=context,
            problem=f"Path {value!r} is not inside {str(self.root)!r}.",
            how_to_fix=f"Provide a path located inside {str(self.root)!r}.",
        )


_DESIGN_NOTES = """
# IsWithin — The Path-Traversal Guard as a Rule

## Purpose
`IsWithin(output_root)` as a pipeline gate (`IsWithin("out") >> WriteStep()`)
or a check on any computed path before it is written to.

## Defaults Are the Safe Ones
Symlinks are resolved and a path equal to the root counts as inside. Both are
options; a filter over scanner output (already normalized) can pass
`resolve_symlinks=False` to skip the syscalls.

## The Root Is Stored As Given
`root` is not normalized at construction: a relative root keeps meaning
"relative to the working directory *at evaluation time*", the same as every
other function in the library. The description shows it as written.

## Constructor Guards
A blank or non-path root, and non-bool options, are `ParamError`s. The root
is judged by the same `to_path` the evaluation uses.
"""
