import os
from pathlib import Path
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._validations import raise_normalize_path_error


@validate_call
def normalize_path(
    path: PathLike,
    *,
    resolve_symlinks: bool = True,
) -> Path:
    """Normalize a path into an absolute, user-expanded `Path`.

    Args:
        path: The path to normalize.
        resolve_symlinks: If True (default), symlinks are followed and the
            real location is returned. If False, the result is only made
            absolute and `..`/`.` are collapsed lexically — symlinks stay
            as they are.

    Returns:
        An absolute `Path` — `~` expanded, relative components collapsed
        and (by default) symlinks resolved. The path does not have to exist.

    Raises:
        AccessError: If the path cannot be resolved (an OS-level error, a
            symlink loop, or invalid text such as an embedded null byte).
    """

    # 1. A null byte is invalid in every path — report it the same way in both modes
    if "\0" in str(path):
        raise_normalize_path_error(path, ValueError("embedded null byte"))

    # 2. Expand user (~) and make the path absolute
    try:
        expanded = Path(path).expanduser()

        # 2.1 Follow symlinks and collapse ".." through the real filesystem
        if resolve_symlinks:
            return expanded.resolve()

        # 2.2 Purely lexical — absolute and collapsed, symlinks untouched
        return Path(os.path.abspath(expanded))

    # 3. Catch OS-level failures, symlink loops and invalid path text
    except (OSError, RuntimeError, ValueError) as caught_exc:
        raise_normalize_path_error(path, caught_exc)


_DESIGN_NOTES = """
# normalize_path — the Library's Single Path Normalizer

## Purpose
Every function that touches the disk starts here, so all of them agree on
what "the same path" means. It does not require the path to exist.

---

## 1. Moved From `validators/`, Gained `resolve_symlinks`
The function itself is unchanged. The new keyword `resolve_symlinks=False`
covers the case where a symlinked location must be kept as written
(`data -> /mnt/storage` stays `data`, not `/mnt/storage`). The default keeps
the old behavior, which the scanners rely on: `collect_paths` resolves its
root, so entries and any root passed to `rebase_path`/`relativize_path`
agree only if both are resolved the same way.

## 2. Why the Null Byte Is Checked Explicitly
`Path.resolve()` raises `ValueError` for it, but `os.path.abspath` (the
non-resolving branch) does not. Checking first makes both modes fail
identically, with the same card.

## 3. Why `RuntimeError` Is Caught
Before Python 3.13 a symlink loop surfaces from `resolve()` as
`RuntimeError`, afterwards as `OSError`; an unknown `~user` is also a
`RuntimeError`. Catching all three keeps the card stable across versions.

## 4. Errors Are `AccessError`, Not `ValidationError`
A bad *type* or a blank string never gets here — the `PathLike` annotation
rejects it with a `ValidationError` before the body runs. What remains is
the environment refusing to resolve a well-formed path.
"""
