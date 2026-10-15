from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_dirs


CollectDirs = create_action(
    collect_dirs,
    main_param="root_dir",
    class_name="CollectDirs",
)
"""Action wrapping `collect_dirs` — collects only the directories of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectDirs — Action Over `collect_dirs`

## Purpose
"Which folders exist under here" as a pipeline step. The root itself is not included.

## Logging
Logging stays on (the `create_action` default). The result is a list that can hold tens of thousands of paths,
but `log_this` shortens large arguments and results (10 items per container plus the total count), so one call
writes a short record instead of the whole list.
"""
