from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from .change_suffix import change_suffix
from .normalize_path import normalize_path
from ._validations import raise_path_not_within_root_error


@validate_call
def rebase_path(
    path: PathLike,
    *,
    source_root: PathLike,
    target_root: PathLike,
    new_suffix: str | None = None,
) -> Path:
    """Map a path inside one root directory to the same place inside another.

    `src/pkg/a.py` with `source_root="src"`, `target_root="out"` becomes
    `out/pkg/a.py` — the "where does the output of this input go" step of
    an extraction pipeline. Nothing is created on the disk.

    Args:
        path: The path inside `source_root`.
        source_root: The directory `path` currently lives in.
        target_root: The directory the result should live in.
        new_suffix: If given, the suffix of the result is replaced (see
            `change_suffix`); `None` keeps the original name.

    Returns:
        The rebased, normalized `Path`.

    Raises:
        ParamError: If `path` is not located inside `source_root`, or
            `new_suffix` is malformed.
        AccessError: If any of the paths cannot be normalized.
    """

    # 1. Normalize all three paths the same way, so they are comparable
    normalized_path = normalize_path(path)
    normalized_source = normalize_path(source_root)
    normalized_target = normalize_path(target_root)

    # 2. Express the path relative to the source root
    try:
        relative = normalized_path.relative_to(normalized_source)
    except ValueError:
        raise_path_not_within_root_error(normalized_path, normalized_source)

    # 3. Re-attach the relative part to the target root
    rebased = normalized_target / relative

    # 4. Optionally replace the suffix
    if new_suffix is not None:
        return change_suffix(rebased, new_suffix)
    return rebased


_DESIGN_NOTES = """
# rebase_path — Source Tree to Target Tree

## Purpose
The path arithmetic behind "mirror this tree somewhere else": each
collected input path is mapped to its output path, keeping the structure
below the root and optionally swapping the extension (`.py` → `.md`).

## Pure Path Arithmetic
No directory is created and nothing is checked for existence. Creating the
parent directory is a separate, explicit step (`ensure_parent_dir`), so a
pipeline can compute all targets first, check them, and only then write.

## `new_suffix=None` vs `""`
`None` means "keep the name as is"; an empty string means "remove the
suffix" — two different, both meaningful requests, which is why the
default is not an empty string.
"""
