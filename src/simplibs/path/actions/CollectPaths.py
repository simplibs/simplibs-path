from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_paths


CollectPaths = create_action(
    collect_paths,
    main_param="root_dir",
    class_name="CollectPaths",
    use_logging=False,
)
"""Action wrapping `collect_paths` — collects files and/or directories of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectPaths — Action Over `collect_paths`

## Purpose
The head of an extraction pipeline: the root goes in, a sorted list of paths comes out.

## Logging Is Off
The result is a list that can hold tens of thousands of paths, and the `log_this` layer would record all of it.
Remove `use_logging=False` once `log_this` is known to truncate large results.
"""
