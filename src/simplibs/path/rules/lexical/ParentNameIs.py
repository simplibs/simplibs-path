from pathlib import Path
# Outers
from .._helpers import PathPartIs


class ParentNameIs(PathPartIs):
    """The name of the directory directly containing the path must satisfy the given rule.

    Rule:
        rule(path.parent.name)

    Example:
        validate(path, ParentNameIs(Equals("tests")))
    """

    __slots__ = ()

    _part_name = "parent name"

    @staticmethod
    def _get_part(path: Path) -> str:
        return path.parent.name


_DESIGN_NOTES = """
# ParentNameIs — The Folder a File Lives In

## Purpose
"Only files inside a folder called `tests`": `ParentNameIs(Equals("tests"))`.
Only the *directly* containing folder is examined.

## No Directory Part Means an Empty Name
`Path("a.txt").parent.name` is `""` — the path says nothing about where it
lives. Rules judging the empty string fail unless they accept it. Paths
produced by the scanners are absolute, so this arises only for hand-written
relative paths; normalize first (`NormalizePath`) if it matters.
"""
