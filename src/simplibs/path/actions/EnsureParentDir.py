from simplibs.actions import create_action
# Outers
from ..logic.ensure import ensure_parent_dir


EnsureParentDir = create_action(
    ensure_parent_dir,
    main_param="path",
    class_name="EnsureParentDir",
)
"""Action wrapping `ensure_parent_dir` — guarantees the directory a path lives in exists, and passes the path on."""


_DESIGN_NOTES = """
# EnsureParentDir — Action Over `ensure_parent_dir`

## Purpose
The step right before a write: `RebasePath(...) >> EnsureParentDir() >> write_step`. The value flowing on is the
file path itself, not its folder.
"""
