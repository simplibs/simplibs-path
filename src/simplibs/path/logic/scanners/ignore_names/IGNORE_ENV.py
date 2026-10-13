from typing import Final


IGNORE_ENV: Final[frozenset[str]] = frozenset({
    ".direnv",
    ".env",
    ".poetry",
    ".venv",
    ".virtualenv",
    "__pypackages__",
    "node_modules",
    "venv",
})
"""Virtual environments and installed dependencies — plus the `.env` secrets file."""


_DESIGN_NOTES = """
# IGNORE_ENV — Environments and Dependencies

## Purpose
Installed third-party code (`venv`, `node_modules`, `__pypackages__`) dwarfs
the project itself and is never part of its sources.

## What Changed
* **`env` moved to `IGNORE_GENERIC`.** Too common as an ordinary folder name
  (`src/env/`, `config/env/`) to be hidden by default.
* **`.env` stays, and now works.** It is usually a *file* (dotenv secrets).
  The old directory-only ignore never matched it; names now apply to files
  too, so a scan no longer picks up secrets by accident.
* Added `.direnv` and `__pypackages__` (PEP 582).
"""
