from pathlib import Path
from typing import Any
# Outers
from ...logic.checks._helpers import to_path
from .._helpers import PathPartIs, build_path_rule_exception


class AnyParentNameIs(PathPartIs):
    """The name of at least one folder above the path must satisfy the given rule.

    Rule:
        any(rule(parent.name) for parent in path.parents)

    Example:
        validate(path, AnyParentNameIs(Equals("tests")))     # tests/a.py and tests/unit/a.py
        exclude_filter = AnyParentNameIs(StartsWith("."))    # anything inside a dot folder
    """

    __slots__ = ()

    _part_name = "any parent name"

    # ----------------------------------------------------------------------
    # Part extraction (every folder name above the path, the nearest first)
    # ----------------------------------------------------------------------
    @staticmethod
    def _get_parts(path: Path) -> list[str]:

        # 1. The root, the drive and the current folder (`.`) have no name; `..` is a step, not a name
        return [parent.name for parent in path.parents if parent.name not in ("", "..")]

    # ----------------------------------------------------------------------
    # Rule definition
    # ----------------------------------------------------------------------
    def is_valid(self, value: Any) -> bool:

        # 1. Anything that cannot be turned into a path fails
        path = to_path(value)
        if path is None:
            return False

        # 2. One folder name that satisfies the wrapped rule is enough
        return any(self.rule.is_valid(name) for name in self._get_parts(path))

    # ----------------------------------------------------------------------
    # Exception definition
    # ----------------------------------------------------------------------
    def build_exception(
        self,
        value: Any,
        value_name: str | None = None,
        context: str | None = None,
    ) -> Exception:

        # 1. The folder names the rule was tried on (a value that is not a path has none)
        path = to_path(value)
        names = self._get_parts(path) if path is not None else []

        # 2. What is wrong: no folder at all, or no folder that fits
        if names:
            problem = f"None of the folders above the path ({', '.join(repr(n) for n in names)}) satisfies the rule."
        else:
            problem = f"Path {value!r} has no folder above it to examine."

        # 3. Build the exception (the not-a-path branch is handled by the helper)
        return build_path_rule_exception(
            error_name="ANY_PARENT_NAME_IS_ERROR",
            expected=f"a path with {self.describe()}",
            value=value,
            value_name=value_name,
            context=context,
            problem=problem,
            how_to_fix="Provide a path that lies inside a folder whose name satisfies the rule.",
        )


_DESIGN_NOTES = """
# AnyParentNameIs — Somewhere Inside a Folder of That Name

## Purpose
"Everything inside a folder called `tests`": `AnyParentNameIs(Equals("tests"))`
takes `tests/a.py` and `tests/unit/deep/a.py` alike. `ParentNameIs` looks at
the folder directly containing the path and nothing above it; this rule looks
at all of them.

## Why It Takes a Rule, Not a List of Names
The same reason as `NameIs`: every string rule already exists. A set of names
is `AnyParentNameIs(IsIn((".git", "node_modules")))`, a prefix is
`AnyParentNameIs(StartsWith("."))`, a pattern is `AnyParentNameIs(Regex(...))`.

## Which Names Are Judged
Every folder above the path, the nearest first. The root, the drive and the
current folder (`.`) have no name, and `..` is a step to the parent, not a
name — none of them is judged. The path itself is not judged either: its own
name is the business of `NameIs`.

## A Path Without a Folder Fails
`Path("a.py")` has nothing above it, so no name can satisfy the rule — the
same as an empty name does with `ParentNameIs`. Paths from the scanners are
absolute; normalize a hand-written relative path first if it matters.

## Text Only
Nothing is read from the disk: the folder names come from the text of the
path. A symlink is not followed, so a folder reached through a link is judged
by the name it was reached by.

## The Failure Card Is Its Own
`NameIs` hands over the card of the wrapped rule, because one name failed. Here
no single name is to blame — every folder failed — so the card says so and lists
the names that were tried (`ANY_PARENT_NAME_IS_ERROR`). A value that is not a
path at all gets the shared "not a path" card.
"""
