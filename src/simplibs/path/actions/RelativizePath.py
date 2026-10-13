from simplibs.actions import create_action
# Outers
from ..logic.transformers import relativize_path


RelativizePath = create_action(
    relativize_path,
    main_param="path",
    class_name="RelativizePath",
)
"""Action wrapping `relativize_path` — expresses a path relative to `root`."""


_DESIGN_NOTES = """
# RelativizePath — Action Over `relativize_path`

## Purpose
Shows a collected path as it appears inside the scanned tree (`src/a/b.py` instead of the absolute path).

## Configuration
`RelativizePath(root=...)` — `root` is required. A path outside it raises a `ParamError` when the action runs.
"""
