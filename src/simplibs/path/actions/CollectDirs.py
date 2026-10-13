from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_dirs


CollectDirs = create_action(
    collect_dirs,
    main_param="root_dir",
    class_name="CollectDirs",
    use_logging=False,
)
"""Action wrapping `collect_dirs` — collects only the directories of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectDirs — Action Over `collect_dirs`

## Purpose
"Which folders exist under here" as a pipeline step. The root itself is not included.

## Logging Is Off
The result is a list that can hold tens of thousands of paths, and the `log_this` layer would record all of it.
Remove `use_logging=False` once `log_this` is known to truncate large results.
"""
