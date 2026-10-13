from pathlib import Path
# Outers
from .._helpers import PathPartIs


class StemIs(PathPartIs):
    """The final name of a path without its last suffix (`report`) must satisfy the given rule.

    Rule:
        rule(path.stem)

    Example:
        validate(path, StemIs(Contains("draft")))
    """

    __slots__ = ()

    _part_name = "stem"

    @staticmethod
    def _get_part(path: Path) -> str:
        return path.stem


_DESIGN_NOTES = """
# StemIs — The Name Without Its Extension

## Purpose
`NameIs(Contains("py"))` matches `a.py`, because the *extension* contains
"py". `StemIs` judges only the part before the last suffix — what people
usually mean when they talk about "the name of the file".

## Compound Names
`Path("archive.tar.gz").stem` is `archive.tar` (only the last suffix is
removed). That is pathlib's definition and is kept as is.
"""
