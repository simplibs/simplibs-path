from simplibs.actions import create_action
# Outers
from ..logic.transformers import change_suffix


ChangeSuffix = create_action(
    change_suffix,
    main_param="path",
    class_name="ChangeSuffix",
)
"""Action wrapping `change_suffix` — replaces, adds or removes the last suffix of a path."""


_DESIGN_NOTES = """
# ChangeSuffix — Action Over `change_suffix`

## Purpose
`ChangeSuffix(new_suffix=".md")` as one named step of a pipeline.

## Call-Time Shape Check
`new_suffix` is a plain `str` at construction; its shape (leading dot, no separators) is checked by the
function when the action runs.
"""
