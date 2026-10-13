from simplibs.actions import create_action
# Outers
from ..logic.transformers import normalize_path


NormalizePath = create_action(
    normalize_path,
    main_param="path",
    class_name="NormalizePath",
)
"""Action wrapping `normalize_path` — makes a path absolute, `~`-expanded and (by default) symlink-resolved."""


_DESIGN_NOTES = """
# NormalizePath — Action Over `normalize_path`

## Purpose
The first step of most path pipelines (`NormalizePath() >> EnsureDir() >> CollectFiles()`), so every later
step sees one canonical form of the path.

## Configuration
`NormalizePath(resolve_symlinks=False)` keeps symlinks as written. The main input is the path; the result is a `Path`.
"""
