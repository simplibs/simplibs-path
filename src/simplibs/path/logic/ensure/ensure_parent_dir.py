from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
from ..transformers import normalize_path
# Inners
from .ensure_dir import ensure_dir


@validate_call
def ensure_parent_dir(
    path: PathLike,
) -> Path:
    """Guarantee that the directory a path lives in exists — without creating the path itself.

    The step right before writing an output file: the file is not there
    yet, but its folder must be.

    Args:
        path: The path (usually of a file about to be written).

    Returns:
        The normalized `Path` itself — not its parent — so the call can be
        chained straight into the write.

    Raises:
        StateError: If a file occupies the place of a needed directory.
        AccessError: If the parent directory cannot be created.
    """

    # 1. Normalize the target path
    normalized_path = normalize_path(path)

    # 2. Guarantee its parent directory (and everything above it)
    ensure_dir(normalized_path.parent)

    # 3. Return the path itself, ready for writing
    return normalized_path


_DESIGN_NOTES = """
# ensure_parent_dir — the Step Before Writing

## Purpose
Writing `out/pkg/a.md` fails when `out/pkg/` is missing, and creating the
*file* up front (what `ensure_file` does) is wrong when the writer wants to
create it itself — with its own content, mode or encoding. This function
prepares only the folder.

## Returns the Path, Not the Parent
In a pipeline the value flowing on is the file's path:
`RebasePath(...) >> EnsureParentDir() >> write_step`. Returning the parent
would force every caller to rebuild the path they started with.

## Pure Composition
No logic of its own: `normalize_path` and `ensure_dir` do the work, so the
two stay the single source of truth for what "normalized" and "exists" mean.
"""
