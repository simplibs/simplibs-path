from typing import NoReturn
from simplibs.exception import ParamError


def raise_nothing_to_collect_error() -> NoReturn:
    """Raise ParamError when both `collect_files` and `collect_dirs` are False."""

    # 1. Raise structured ParamError wrapping a ValueError
    raise ParamError(
        error_name="NOTHING_TO_COLLECT",
        label="collect_files, collect_dirs",
        value="collect_files=False, collect_dirs=False",
        problem=(
            "Both collect_files and collect_dirs are False.",
            "Nothing could ever be collected, so the scan would be pointless.",
        ),
        expected="At least one of collect_files or collect_dirs set to True.",
        how_to_fix=(
            "Set collect_files=True to collect files.",
            "Set collect_dirs=True to collect directories.",
        ),
        exception=ValueError,
    )


_DESIGN_NOTES = """
# raise_nothing_to_collect_error — Contradictory Collect Flags

## Purpose
An earlier `collect_paths` returned `[]` for this combination before even
checking the root — silently, and even for a root that does not exist. Both
flags off is almost certainly a caller mistake, so it is now reported
immediately instead of producing an empty result that looks like success.
"""
