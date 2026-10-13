from pathlib import Path
# Outers
from .._helpers import PathPartIs


class NameIs(PathPartIs):
    """The final name of a path (`report.txt`) must satisfy the given rule.

    Rule:
        rule(path.name)

    Example:
        validate(path, NameIs(StartsWith("test_")))
        exclude_filter = NameIs(Regex(r"^\\d+\\."))
    """

    __slots__ = ()

    _part_name = "name"

    @staticmethod
    def _get_part(path: Path) -> str:
        return path.name


_DESIGN_NOTES = """
# NameIs — Any String Rule, Pointed at a File Name

## Purpose
`NameIs(StartsWith("test_"))`, `NameIs(Regex(...))`, `NameIs(HasLength(...))`
— the whole string-rule vocabulary applies to file names without a single
path-specific copy of it.

## Everything Shared Lives in `PathPartIs`
See its notes: wrapping of plain callables, the delegated failure card
(labelled `source.name`), the `name: <rule>` description.
"""
