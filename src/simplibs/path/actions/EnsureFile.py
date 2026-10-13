from simplibs.actions import create_action
# Outers
from ..logic.ensure import ensure_file


EnsureFile = create_action(
    ensure_file,
    main_param="path",
    class_name="EnsureFile",
)
"""Action wrapping `ensure_file` — guarantees a file (and its parent directory) exists."""


_DESIGN_NOTES = """
# EnsureFile — Action Over `ensure_file`

## Purpose
`EnsureFile(create=False)` is also a pure precondition: it passes an existing file on, or raises `NotFoundError`.
"""
