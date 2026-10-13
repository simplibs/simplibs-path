from typing import Final


IGNORE_GENERIC: Final[frozenset[str]] = frozenset({
    "_build",
    "build",
    "dist",
    "env",
    "out",
    "site",
    "target",
})
"""Common output-folder names that can also be ordinary source folders.

NOT part of `DEFAULT_IGNORE_NAMES` — opt in explicitly:
`ignore_names=DEFAULT_IGNORE_NAMES | IGNORE_GENERIC`.
"""


_DESIGN_NOTES = """
# IGNORE_GENERIC — Opt-In, Because the Names Are Ambiguous

## Purpose
`build/`, `dist/`, `site/`, `target/` are the output folders of setuptools,
MkDocs, Cargo and Maven — but `src/site/`, `docs/build-notes/`-style
folders and a package literally named `env` exist too. A scan that hides
them by default loses content without saying so, which is worse than a scan
that is a bit noisy. This set exists so that dropping them is a conscious,
one-expression choice.
"""
