from simplibs.actions import create_action
# Outers
from ..logic.scanners import filter_paths


FilterPaths = create_action(
    filter_paths,
    main_param="paths",
    class_name="FilterPaths",
)
"""Action wrapping `filter_paths` — keeps the paths of a list that satisfy a Rule or callable."""


_DESIGN_NOTES = """
# FilterPaths — Action Over `filter_paths`

## Purpose
`CollectFiles() >> FilterPaths(rule=HasSuffix(".py") & ~IsHidden())`.

## `rule` Is Required
A filter without a rule would only copy the list. The main input is a collection of paths (not a generator).

## Logging
Logging stays on (the `create_action` default). The result is a list that can hold tens of thousands of paths,
but `log_this` shortens large arguments and results (10 items per container plus the total count), so one call
writes a short record instead of the whole list.
"""
