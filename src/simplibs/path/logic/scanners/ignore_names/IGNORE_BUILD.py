from typing import Final


IGNORE_BUILD: Final[frozenset[str]] = frozenset({
    "*.egg-info",
    ".cache",
    ".coverage",
    ".coverage.*",
    ".eggs",
    ".gradle",
    ".hypothesis",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".next",
    ".nox",
    ".nuxt",
    ".pytest_cache",
    ".pytype",
    ".ruff_cache",
    ".serverless",
    ".terraform",
    ".tox",
    "__pycache__",
    "htmlcov",
})
"""Caches, coverage data and tool output that are unambiguous by name.

Entries containing `*`, `?` or `[` are glob patterns (`*.egg-info`).
"""


_DESIGN_NOTES = """
# IGNORE_BUILD — Generated Artifacts With Unmistakable Names

## Purpose
Everything here is produced by a tool, never written by hand, and its name
says so (`__pycache__`, `.mypy_cache`, `htmlcov`).

## What Changed
* **`build`, `dist`, `site`, `_build` moved to `IGNORE_GENERIC`.** They are
  real output folders in many projects but also ordinary source folders in
  others; hiding them by default silently dropped legitimate content.
* **`.coverage` now works** (it is a file) and `.coverage.*` covers the
  parallel-run files; `*.egg-info` is a glob, which the exact-name matching
  of the old version could not express.
* Added `.cache`, `.eggs`, `.gradle`, `.hypothesis`, `.ipynb_checkpoints`,
  `.pytype`, `.terraform`.
"""
