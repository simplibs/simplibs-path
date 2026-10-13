from .DEFAULT_IGNORE_NAMES import DEFAULT_IGNORE_NAMES
from .IGNORE_BUILD import IGNORE_BUILD
from .IGNORE_ENV import IGNORE_ENV
from .IGNORE_GENERIC import IGNORE_GENERIC
from .IGNORE_IDE import IGNORE_IDE
from .IGNORE_SYSTEM import IGNORE_SYSTEM
from .IGNORE_VCS import IGNORE_VCS


_DESIGN_NOTES = """
# Scanner Ignore Names Sub-Package

## Purpose
Named sets of entry names (files and directories) that scanners skip. Names
containing `*`, `?` or `[` are glob patterns; all others match exactly
(case-insensitively on Windows). Renamed from `ignore_dirs`, because the
sets contain files too.

## Internal Components Registry

| Component              | Type     | Description                                                       |
| :--------------------- | :------- | :---------------------------------------------------------------- |
| `DEFAULT_IGNORE_NAMES` | Constant | Union of VCS, ENV, BUILD, IDE and SYSTEM — the scanners' default. |
| `IGNORE_BUILD`         | Constant | Caches, coverage data and tool output with unmistakable names.    |
| `IGNORE_ENV`           | Constant | Virtual environments, installed dependencies, `.env`.             |
| `IGNORE_GENERIC`       | Constant | Ambiguous output-folder names (`build`, `dist`, ...) — opt-in.    |
| `IGNORE_IDE`           | Constant | Editor and IDE settings.                                          |
| `IGNORE_SYSTEM`        | Constant | OS housekeeping (`.DS_Store`, `Thumbs.db`, ...).                  |
| `IGNORE_VCS`           | Constant | Version control metadata (`.git`, `.svn`, ...).                   |
"""
