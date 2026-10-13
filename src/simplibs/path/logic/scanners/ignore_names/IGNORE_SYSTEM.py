from typing import Final


IGNORE_SYSTEM: Final[frozenset[str]] = frozenset({
    "$RECYCLE.BIN",                 # Windows recycle bin
    ".DS_Store",                    # macOS folder metadata
    ".fseventsd",                   # macOS file system events log
    ".Spotlight-V100",              # macOS Spotlight index
    ".TemporaryItems",              # macOS temporary items
    ".Trashes",                     # macOS trash directory
    "System Volume Information",    # Windows volume metadata
    "Thumbs.db",                    # Windows thumbnail cache
    "desktop.ini",                  # Windows folder customization
    "ehthumbs.db",                  # Windows Media Center thumbnails
})
"""Operating-system housekeeping files and folders (both files and directories)."""


_DESIGN_NOTES = """
# IGNORE_SYSTEM — OS Housekeeping

## Purpose
Entries the operating system creates on its own. Most are *files*
(`.DS_Store`, `Thumbs.db`) — the reason the ignore mechanism now applies to
files as well as directories; previously this whole group was dead.

## Windows Coverage
`$RECYCLE.BIN` and `System Volume Information` matter when scanning from the
root of a drive; they are unreadable for normal users anyway.
"""
