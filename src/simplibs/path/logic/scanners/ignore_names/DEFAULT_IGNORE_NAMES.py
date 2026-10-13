from typing import Final
# Inners
from .IGNORE_BUILD import IGNORE_BUILD
from .IGNORE_ENV import IGNORE_ENV
from .IGNORE_IDE import IGNORE_IDE
from .IGNORE_SYSTEM import IGNORE_SYSTEM
from .IGNORE_VCS import IGNORE_VCS


DEFAULT_IGNORE_NAMES: Final[frozenset[str]] = (
    IGNORE_VCS
    | IGNORE_ENV
    | IGNORE_BUILD
    | IGNORE_IDE
    | IGNORE_SYSTEM
)
"""The names every scan skips unless told otherwise.

Extend it with a union: `DEFAULT_IGNORE_NAMES | {"my_dir"}`.
"""


_DESIGN_NOTES = """
# DEFAULT_IGNORE_NAMES — the Scanners' Default

## Purpose
The union of every group that is safe to hide without surprising anyone:
version control, environments, generated artifacts with unmistakable names,
IDE settings and OS housekeeping. `IGNORE_GENERIC` is deliberately not
included (see its notes).

## A `frozenset` So the Default Is Safe
A mutable default shared by every call could be changed by accident
(`DEFAULT_IGNORE_NAMES.add(...)`) and affect all later scans. A frozenset
cannot, and `|` still builds a new, extended one.
"""
