from pathlib import Path
from typing import NoReturn
from simplibs.exception import AccessError


def raise_collect_paths_root_unreadable_error(
    path: Path,
    caught_exc: Exception,
) -> NoReturn:
    """Raise AccessError when the scan root exists but its entries cannot be listed."""

    # 1. Raise structured AccessError wrapping the caught OS exception
    raise AccessError(
        error_name="COLLECT_PATHS_ROOT_UNREADABLE",
        label=f"root directory '{path}'",
        value=str(path),
        problem=(
            f"Cannot list the entries of '{path}'.",
            f"OS reported: {caught_exc}",
        ),
        expected="A root directory the current user is allowed to read.",
        how_to_fix=(
            f"Check read and execute permissions of '{path}'.",
            "Scan a directory you have access to, or run with sufficient permissions.",
        ),
        exception=type(caught_exc),
    )


_DESIGN_NOTES = """
# raise_collect_paths_root_unreadable_error — Unreadable Scan Root

## Purpose
Unreadable *sub*directories are skipped silently while walking — a normal
tree always contains a few. An unreadable *root* is different: skipping it
would return an empty result that looks exactly like "nothing found". The
scanners check the root up front and report this card instead.
"""
