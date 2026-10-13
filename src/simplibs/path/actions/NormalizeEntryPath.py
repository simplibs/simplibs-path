from simplibs.actions import create_action
# Outers
from ..logic.transformers import normalize_entry_path


NormalizeEntryPath = create_action(
    normalize_entry_path,
    main_param="path",
    class_name="NormalizeEntryPath",
)
"""Action wrapping `normalize_entry_path` — resolves an entry's folder and keeps its own name as written."""


_DESIGN_NOTES = """
# NormalizeEntryPath — Action Over `normalize_entry_path`

## Purpose
The first step of pipelines that act on the entry itself (delete, move, rename)
rather than on its content — `NormalizeEntryPath() >> DeleteFile()`.
"""
