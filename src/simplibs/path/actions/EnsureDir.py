from simplibs.actions import create_action
# Outers
from ..logic.ensure import ensure_dir


EnsureDir = create_action(
    ensure_dir,
    main_param="path",
    class_name="EnsureDir",
)
"""Action wrapping `ensure_dir` — guarantees a directory (and its parents) exists."""


_DESIGN_NOTES = """
# EnsureDir — Action Over `ensure_dir`

## Purpose
Turns "I need this folder" into a pipeline step that passes the normalized directory on.

## Changes the Disk
Together with `EnsureFile` and `EnsureParentDir`, the only actions that do.
"""
