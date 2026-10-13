from simplibs.actions import create_action
# Outers
from ..logic.transformers import rebase_path


RebasePath = create_action(
    rebase_path,
    main_param="path",
    class_name="RebasePath",
)
"""Action wrapping `rebase_path` — maps a path from `source_root` to the same place under `target_root`."""


_DESIGN_NOTES = """
# RebasePath — Action Over `rebase_path`

## Purpose
The "where does the output of this input go" step:
`RebasePath(source_root="src", target_root="out", new_suffix=".md")`.

## Configuration
`source_root` and `target_root` are required; `new_suffix` is optional (`None` keeps the name, `""` removes the
suffix). Pure path arithmetic — pair it with `EnsureParentDir` before writing.
"""
