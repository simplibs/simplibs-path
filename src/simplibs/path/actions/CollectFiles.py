from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_files


CollectFiles = create_action(
    collect_files,
    main_param="root_dir",
    class_name="CollectFiles",
    use_logging=False,
)
"""Action wrapping `collect_files` — collects only the files of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectFiles — Action Over `collect_files`

## Purpose
Real locking: the type flags are not part of `collect_files`' signature, so `CollectFiles` cannot be made to
collect directories. (The former `functools.partial` preset only changed defaults.)

## Logging Is Off
The result is a list that can hold tens of thousands of paths, and the `log_this` layer would record all of it.
Remove `use_logging=False` once `log_this` is known to truncate large results.
"""
