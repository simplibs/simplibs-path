from typing import Any, NoReturn
from simplibs.exception import AccessError


def raise_normalize_path_error(
    path: Any,
    caught_exc: Exception,
) -> NoReturn:
    """Raise AccessError when path normalization or resolution fails."""

    # 1. Raise structured AccessError wrapping the caught resolution exception instance
    raise AccessError(
        error_name="PATH_NORMALIZATION_FAILED",
        label=f"path '{path}'",
        value=str(path),
        problem=(
            f"Could not resolve or normalize path '{path}'.",
            # "The underlying operating system or resolver reported an error.",
            f"OS reported: {caught_exc}",
        ),
        expected="A valid path string or Path instance that can be resolved on this system.",
        how_to_fix=(
            "Check for recursive or circular symlinks on the path.",
            "Ensure the path contains no null bytes or characters invalid for the operating system.",
            "Ensure the path format is valid for the operating system.",
        ),
        exception=caught_exc,
    )


_DESIGN_NOTES = """
# raise_normalize_path_error — normalize_path Failure Diagnostic

## Purpose
Single point of failure for "the path could not be resolved". Raised from
`normalize_path` for OS-level errors, symlink loops (`RuntimeError` before
Python 3.13, `OSError` after) and invalid path text such as an embedded null
byte (`ValueError`).

## Renamed From `raise_ensure_normalize_path_error`
`normalize_path` ensures nothing — the old `ensure` prefix was a leftover of
the former `validators/` folder. Only the name and one added how-to-fix
line (null bytes) changed.
"""