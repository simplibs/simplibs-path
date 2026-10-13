from typing import Final


IGNORE_IDE: Final[frozenset[str]] = frozenset({
    ".fleet",       # JetBrains Fleet
    ".idea",        # PyCharm / JetBrains IDEs
    ".settings",    # Eclipse
    ".vs",          # Visual Studio
    ".vscode",      # Visual Studio Code
})
"""Editor and IDE project settings."""


_DESIGN_NOTES = """
# IGNORE_IDE — Editor Settings

## Purpose
Per-project IDE state: personal, machine-specific and not part of the
sources. Only `.fleet` is new compared to the former version.
"""
