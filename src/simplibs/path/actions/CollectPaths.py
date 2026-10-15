from simplibs.actions import create_action
# Outers
from ..logic.scanners import collect_paths


CollectPaths = create_action(
    collect_paths,
    main_param="root_dir",
    class_name="CollectPaths",
)
"""Action wrapping `collect_paths` — collects files and/or directories of a tree into a sorted list."""


_DESIGN_NOTES = """
# CollectPaths — Action Over `collect_paths`

## Purpose
The head of an extraction pipeline: the root goes in, a sorted list of paths comes out.

## Logging
Logging stays on (the `create_action` default). The result is a list that can hold tens of thousands of paths,
but `log_this` shortens large arguments and results (10 items per container plus the total count), so one call
writes a short record instead of the whole list.
"""
