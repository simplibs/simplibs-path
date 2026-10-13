from pathlib import Path
from simplibs.types import str_not_blank


PathLike = str_not_blank | Path
"""A filesystem path given as a non-blank string or as a `Path` instance.

The annotation of every path parameter in this library. A blank string is
rejected on purpose: `Path("")` silently means "the current directory",
which is almost never what the caller intended.
"""


_DESIGN_NOTES = """
# PathLike — the accepted shape of a path argument

## Purpose
One shared annotation for every path parameter in `simplibs-path`, so the
accepted input is defined (and described in error cards) in exactly one place.

---

## 1. Why a Blank String Is Rejected

`Path("")` and `Path("   ")` do not fail — they quietly become `.` (the
current working directory). `ensure_dir("")` would "succeed" and
`collect_paths("")` would scan whatever directory the process happens to run
in. Rejecting blank strings at the boundary turns that silent surprise into
an immediate, readable error.

## 2. Why `str | Path`, Not `os.PathLike`

Every function normalizes its input through `Path` first. Keeping the
accepted input to the two types people actually pass keeps validation
messages short ("non-blank string | Path") and avoids bytes-based
`os.PathLike` objects, which `Path` cannot represent.

## 3. Not a Rule Input Type

Rules never raise on a wrong input type — they use `to_path` (see
`_helpers/to_path.py`) and answer `False`. This annotation is for the
`@validate_call` boundary of functions only.
"""
