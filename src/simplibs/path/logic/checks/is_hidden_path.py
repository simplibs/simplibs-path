import os
import stat
from simplibs.validate import validate_call
# Outers
from ...annotations import PathLike
# Inners
from ._helpers import to_path

@validate_call
def is_hidden_path(
    path: PathLike,
    *,
    check_attributes: bool = False,
    _validate_call: bool = True,
) -> bool:
    """Check whether a path's final name marks it as hidden.

    Args:
        path: The path to check. Only its final name is considered, not the
            directories above it.
        check_attributes: If True, on Windows an existing path that carries
            the "hidden" file attribute also counts. No effect elsewhere.
        _validate_call: Internal bypass switch for `@validate_call` — rules
            pass `False` because they have already checked the input type.

    Returns:
        True if the final name starts with a dot (`.git`, `.env`), or — with
        `check_attributes` on Windows — the hidden attribute is set. `.` and
        `..` are never hidden.
    """

    # 1. Anything that cannot be turned into a path is not hidden
    candidate = to_path(path)
    if candidate is None:
        return False

    # 2. The Unix convention — a leading dot in the final name
    name = candidate.name
    if name.startswith(".") and name not in (".", ".."):
        return True

    # 3. The Windows convention — an attribute on the file, only when asked for
    if check_attributes and os.name == "nt":
        try:
            attributes = getattr(candidate.stat(), "st_file_attributes", 0)
        except OSError:
            return False
        return bool(attributes & stat.FILE_ATTRIBUTE_HIDDEN)

    # 4. Nothing marks it as hidden
    return False


_DESIGN_NOTES = """
# is_hidden_path — Hidden by Name, Optionally by Attribute

## Purpose
The predicate behind `IsHidden`, meant for filters such as
`exclude_filter=IsHidden()`.

---

## 1. Name-Based by Default
The dot convention needs no disk access, which matters in a filter running
over thousands of entries, and it behaves identically on every platform
(`.git` is hidden to a scanner on Windows too).

## 2. The Windows Attribute Is Opt-In
Reading it costs a `stat` call per path, and it only exists on Windows.
`check_attributes=True` asks for it; elsewhere the flag is simply ignored so
the same code runs everywhere.

## 3. Only the Final Name
`/home/me/.config/tool/settings.json` is not "hidden" by this function —
its *name* is not. Whether a file lives under a hidden directory is a
question about the path's parents, which scanners answer by pruning
(`ignore_names`) rather than by testing each entry.
"""
