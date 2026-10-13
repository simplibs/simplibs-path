from simplibs.actions import create_action
# Outers
from ..logic.transformers import make_unique_path


MakeUniquePath = create_action(
    make_unique_path,
    main_param="path",
    class_name="MakeUniquePath",
)
"""Action wrapping `make_unique_path` — returns the path, or a numbered variant of it that does not exist yet."""


_DESIGN_NOTES = """
# MakeUniquePath — Action Over `make_unique_path`

## Purpose
Choosing an output name that overwrites nothing: `RebasePath(...) >> MakeUniquePath()`.

## Not a Reservation
The name is free at the moment of the call; claim it by opening the result with mode `"x"`.
"""
