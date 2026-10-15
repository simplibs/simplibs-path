from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_files


CollectFiles = create_action(
    collect_files,
    main_param="root_dir",
    class_name="CollectFiles",
)
"""Action wrapping `collect_files` — collects only the files of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectFiles — Action Over `collect_files`

## Purpose
Real locking: the type flags are not part of `collect_files`' signature, so `CollectFiles` cannot be made to
collect directories. (The former `functools.partial` preset only changed defaults.)

## Logging
Logging stays on (the `create_action` default). The result is a list that can hold tens of thousands of paths,
but `log_this` shortens large arguments and results (10 items per container plus the total count), so one call
writes a short record instead of the whole list.
"""
