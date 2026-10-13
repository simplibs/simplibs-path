from simplibs.actions import create_action
# Outers
from ..logic.scanners import filter_paths


FilterPaths = create_action(
    filter_paths,
    main_param="paths",
    class_name="FilterPaths",
    use_logging=False,
)
"""Action wrapping `filter_paths` — keeps the paths of a list that satisfy a Rule or callable."""


_DESIGN_NOTES = """
# FilterPaths — Action Over `filter_paths`

## Purpose
`CollectFiles() >> FilterPaths(rule=HasSuffix(".py") & ~IsHidden())`.

## `rule` Is Required
A filter without a rule would only copy the list. The main input is a collection of paths (not a generator).

## Logging Is Off
The result is a list that can hold tens of thousands of paths, and the `log_this` layer would record all of it.
Remove `use_logging=False` once `log_this` is known to truncate large results.
"""
