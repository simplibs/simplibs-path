import tempfile
from pathlib import Path


def can_create_inside(directory: Path) -> bool:
    """Check whether a file can be created inside a directory — and leave no trace.

    Args:
        directory: An existing directory.

    Returns:
        True if an anonymous temporary file could be created (and was
        removed again); False if the OS refused.
    """

    # 1. Create and immediately discard an anonymous temporary file
    try:
        with tempfile.TemporaryFile(dir=directory):
            return True

    # 2. Any permission or OS-level refusal means "not writable"
    except OSError:
        return False


_DESIGN_NOTES = """
# can_create_inside — the Honest Write Probe for a Directory

## Purpose
`os.access(path, W_OK)` is unreliable for directories on Windows (it mostly
reports "yes") and ignores ACLs and read-only mounts everywhere. Actually
creating a file is the only check that matches what a later write will
experience.

## Why It Leaves No Trace
`TemporaryFile` is unlinked on creation on POSIX and opened with
`O_TEMPORARY` on Windows: it never appears under a name that survives, even
if the process is killed in the middle.
"""
