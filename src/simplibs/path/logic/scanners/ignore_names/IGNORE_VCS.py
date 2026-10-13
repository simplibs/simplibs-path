from typing import Final


IGNORE_VCS: Final[frozenset[str]] = frozenset({
    ".bzr",
    ".git",
    ".hg",
    ".svn",
})
"""Metadata directories of version control systems."""


_DESIGN_NOTES = """
# IGNORE_VCS — Version Control Metadata

## Purpose
Names of the directories where Git, Mercurial, Subversion and Bazaar keep
their internals. They hold no project content, often thousands of objects,
and are never what a scan is looking for.

## Unchanged
Same content as the former `ignore_dirs/IGNORE_VCS`; only the package was
renamed (`ignore_dirs` → `ignore_names`).
"""
